{%- extends 'markdown/index.md.j2' -%}

## Add a space after rawcell
{% block rawcell %}
{{ super() }}

{% endblock rawcell %}
