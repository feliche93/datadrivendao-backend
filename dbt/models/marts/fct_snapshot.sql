{{ config(materialized='table') }}

WITH dims_daos AS (
    SELECT *
    FROM {{ ref('dims_daos') }}
)

SELECT
    dims_daos.id AS dao_id,
    followers,
    proposals,
    voters_1d,
    proposals_1d,
    followers_1d
FROM dims_daos
LEFT JOIN {{ source('raw_data', 'snapshot_explore') }} ON snapshot_explore.index = dims_daos.id
LEFT JOIN {{ source('raw_data', 'snapshot_spaces') }} ON snapshot_spaces.id = dims_daos.id
