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
    CAST(
        PARSE_TIMESTAMP(
        "%F",
        SUBSTR(snapshot_explore_scd.scraped_at, 0, 10)
    ) AS DATE) AS scraped_date,
    followers AS total_followers,
    proposals AS total_proposals,
    activeProposals AS active_proposals,
    voters_1d AS voters,
    proposals_1d AS proposals,
    followers_1d AS followers
FROM dim_dao
LEFT JOIN snapshot_explore_scd ON snapshot_explore_scd.index = dim_dao.dao_id