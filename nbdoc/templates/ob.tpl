{%- extends 'markdown/index.md.j2' -%}

## Add a space after rawcell
{% block rawcell %}
{{ super() }}

{% endblock rawcell %}


{% block codecell %}
{% if cell.metadata.script  -%}
<CodeSection file="{{ cell.metadata.filename }}">
{% elif 'magics_language' in cell.metadata  -%}
<CodeSection lang="{{ cell.metadata.magics_language }}">
{% elif 'name' in nb.metadata.get('language_info', {}) -%}
<CodeSection lang="{{ nb.metadata.language_info.name }}">
{% else -%}
<CodeSection>
{%- endif %}
{{ super() }}
</CodeSection>
{% endblock codecell %}


{%- block input_group -%}
<CodeInputBlock>
{{ super() }}
</CodeInputBlock>
{% endblock input_group %}

{%- block output_group -%}
<CodeOutputBlock>
{{ super() }}
</CodeOutputBlock>
{% endblock output_group %}
