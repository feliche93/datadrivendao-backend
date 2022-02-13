{{ config(materialized='table') }}

WITH dim_dao AS (
    SELECT *
    FROM {{ ref('dim_dao') }}
)

SELECT
    dao_id,
    followers,
    proposals,
    voters_1d,
    proposals_1d,
    followers_1d
FROM dim_dao
LEFT JOIN {{ source('raw_data', 'snapshot_explore') }} ON snapshot_explore.index = dim_dao.dao_id
LEFT JOIN {{ source('raw_data', 'snapshot_spaces') }} ON snapshot_spaces.id = dim_dao.dao_id
