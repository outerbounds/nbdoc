{%- extends 'markdown/index.md.j2' -%}

## Add a space after rawcell
{% block rawcell %}
{{ super() }}

{% endblock rawcell %}

{%- block output_group -%}
{%- if 'magics_language' in cell.metadata  -%}
    {%- set lang = cell.metadata.magics_language -%}
{%- elif 'name' in nb.metadata.get('language_info', {}) -%}
    {%- set lang = nb.metadata.language_info.name -%}
{%- endif %}
<OutputSection lang="{{ lang }}">
{{ super() }}
</OutputSection>
{% endblock output_group %}
