{{ config(materialized='table') }}

WITH dim_dao AS (
    SELECT *
    FROM {{ ref('dim_dao') }}
),

snapshot_explore_scd AS (
    SELECT *
    FROM {{ source('raw_data', 'snapshot_explore_scd') }}
)

SELECT
    dao_id,
    snapshot_explore_scd.scraped_at,
    followers,
    proposals,
    activeProposals AS active_proposals,
    voters_1d,
    proposals_1d,
    followers_1d
FROM dim_dao
LEFT JOIN snapshot_explore_scd ON snapshot_explore_scd.index = dim_dao.dao_id