{%- extends 'markdown/index.md.j2' -%}

## Add a space after rawcell
{% block rawcell %}
{{ super() }}

{% endblock rawcell %}


{%- block output_group -%}
{%- if cell.metadata.html_output  %}

<HTMLOutputBlock center="{{ cell.metadata.html_center }}">
{{ super() }}
</HTMLOutputBlock>
{%- else  -%}
    {%- if 'magics_language' in cell.metadata  -%}
        {%- set lang = cell.metadata.magics_language -%}
    {%- elif 'name' in nb.metadata.get('language_info', {}) -%}
        {%- set lang = nb.metadata.language_info.name -%}
    {%- endif %}
<CodeOutputBlock lang="{{ lang }}">
{{ super() }}
</CodeOutputBlock>
{%- endif %}
{% endblock output_group %}