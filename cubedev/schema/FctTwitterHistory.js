cube(`TwitterHistory`, {
  sql: `SELECT * FROM dbt_fvemmer.fct_twitter_history`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started  
  },
  
  joins: {
    
  },
  
  measures: {
    count: {
      type: `count`,
      drillMembers: [daoId, scrapedDate]
    },

        followers: {
      sql: `followers`,
      type: `sum`
    },
    
    friends: {
      sql: `friends`,
      type: `sum`
    },
    
    listed: {
      sql: `listed`,
      type: `sum`
    },
    
    favourites: {
      sql: `favourites`,
      type: `sum`
    },
    
    statuses: {
      sql: `statuses`,
      type: `sum`
    }
  },
  
  dimensions: {
    daoId: {
      sql: `dao_id`,
      type: `string`,
      primaryKey: true
    },
    
    scrapedDate: {
      sql: `PARSE_TIMESTAMP('%Y-%m-%d', STRING(scraped_date))`,
      type: `time`
    }
  }
});
