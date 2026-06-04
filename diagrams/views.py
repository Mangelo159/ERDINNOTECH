import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from .models import Diagram


def editor(request):
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def diagram_list(request):
    if request.method == 'GET':
        diagrams = Diagram.objects.values('id', 'name', 'updated_at')
        return JsonResponse(list(diagrams), safe=False)

    data = json.loads(request.body)
    name = data.get('name', 'Sin nombre').strip() or 'Sin nombre'
    schema = data.get('schema', {'tables': []})
    diagram = Diagram.objects.create(name=name, schema=schema)
    return JsonResponse({'id': diagram.id, 'name': diagram.name}, status=201)


@csrf_exempt
@require_http_methods(['GET', 'PUT', 'DELETE'])
def diagram_detail(request, pk):
    diagram = get_object_or_404(Diagram, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'id': diagram.id,
            'name': diagram.name,
            'schema': diagram.schema,
            'updated_at': diagram.updated_at.isoformat(),
        })

    if request.method == 'PUT':
        data = json.loads(request.body)
        if 'name' in data:
            diagram.name = data['name'].strip() or diagram.name
        if 'schema' in data:
            diagram.schema = data['schema']
        diagram.save()
        return JsonResponse({'id': diagram.id, 'name': diagram.name})

    diagram.delete()
    return JsonResponse({'ok': True})


@require_http_methods(['GET'])
def diagram_sql(request, pk):
    diagram = get_object_or_404(Diagram, pk=pk)
    sql = generate_sql(diagram.schema)
    return JsonResponse({'sql': sql})


def generate_sql(schema):
    tables = schema.get('tables', [])
    blocks = []

    for table in tables:
        name = table.get('id', 'tabla')
        columns = table.get('columns', [])
        col_lines = []

        for col in columns:
            col_name = col.get('name', 'campo')
            col_type = col.get('type', 'text')
            is_pk = col.get('pk', False)
            fk_ref = col.get('fk')

            line = f'    {col_name} {col_type}'
            if is_pk:
                line += ' PRIMARY KEY'
            if fk_ref:
                line += f' REFERENCES {fk_ref}(id)'
            col_lines.append(line)

        cols_sql = ',\n'.join(col_lines)
        block = f'CREATE TABLE IF NOT EXISTS {name} (\n{cols_sql}\n);'
        blocks.append(block)

    return '\n\n'.join(blocks)
