{{ config(materialized='table') }}

WITH dim_daos AS (
    SELECT *
    FROM {{ ref('dim_daos') }}
)

SELECT
    dim_daos.id AS dao_id,
    followers,
    proposals,
    voters_1d,
    proposals_1d,
    followers_1d
FROM dim_daos
LEFT JOIN {{ source('raw_data', 'snapshot_explore') }} ON snapshot_explore.index = dim_daos.id
LEFT JOIN {{ source('raw_data', 'snapshot_spaces') }} ON snapshot_spaces.id = dim_daos.id
