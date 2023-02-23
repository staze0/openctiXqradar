OpenCTI_URL = """https://demo.opencti.io/graphql"""
QRadar_URL = """https://<QRadar_URL>/api/{0}"""
QRadar_referential_name = "<QRadar_referential_name>"

QRadar_headers = """{{
    'SEC':'{0}',
    'Content-Type':'application/json',
    'accept':'application/json'
}}"""

query_IPv4 = """query {{
  stixCyberObservables (
    after: "{0}"
    types: ["IPv4-Addr"]
    orderBy: created_at
    orderMode: desc
    filters: [{1}]
  )
  {{
    pageInfo {{
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
      globalCount
    }}
    edges {{
      node {{
        id
        entity_type
        created_at
        updated_at
        observable_value
        x_opencti_score
        creator {{
          entity_type
          name
        }}
        objectLabel {{
          edges {{
            node {{
              value
            }}
          }}
        }}
      }}
    }}
  }}
}}"""

default_query_filter = """{{
        filterMode: and
        values: "{0}"
        operator: "gt"
        key: created_at
      }}"""

IP_query_filter = """{{
        filterMode: or
        values: {0}
        operator: "eq"
        key: value
      }}"""