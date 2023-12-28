
/*
  Here we are trying to remove all null values from all tables we created to store the data
  at time t iff all values across all columns are null because we assigned NaN while we are 
  creating our DataFrame,
*/

{% set table_names = adapter.get_relation(view='table_%', database='your_database', schema='your_schema') %}

{% for table_name in table_names %}

WITH cleaned_{{ table_name.table_name }} AS (
    SELECT *
    FROM "{{ ref(table_name.table_name) }}"
    WHERE NOT ({{ ', '.join(['"{{ table_name.table_name }}".' ~ column.column_name ~ ' IS NULL' for column in adapter.get_columns(ref(table_name.table_name))]) }})
)
{% endfor %}
-- Union all cleaned tables
SELECT * FROM {% for table_name in table_names %} cleaned_{{ table_name.table_name }} {% if not loop.last %} UNION ALL {% endif %} {% endfor %}

