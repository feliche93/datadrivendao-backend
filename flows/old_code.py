    # TODO: Currently not sure how to handle and fix bring back later
    # spaces_data.drop(columns=["categories", "admins", "members"], inplace=True)

    # TODO: Remove old code when not neeeded
    # normalizing strategy data
    # putting every strategy into it's own column
    # strategy_df = pd.DataFrame(spaces_data["strategies"].to_list(), index=spaces_data.index)
    # strategy_df_columns = [f"strategy_{col+1}" for col in range(len(strategy_df.columns))]
    # strategy_df.columns = strategy_df_columns
    # strategy_df.index = spaces_data.index

    # normalizing nested json into several columns
    # for col in strategy_df_columns:
    #     noramlized_df = pd.json_normalize(strategy_df[col])
    #     noramlized_df = noramlized_df.add_prefix(f"{col}_")
    #     noramlized_df.index = strategy_df.index
    #     strategy_df = strategy_df.join(noramlized_df)

    # dropping nested ones
    # strategy_df.drop(columns=strategy_df_columns, inplace=True)

    # merging strategy data with spaces data for final df
    # spaces_data.drop(columns=["strategies"], inplace=True)
    # spaces_data = spaces_data.join(strategy_df)

    # adding scraping timestamp


    # wr.s3.read_parquet(
    #     path=path,
    #     boto3_session=session,
    # )


    # TODO: Remove old code when not neeeded
    # cleaning strategy data
    # for record in json_data["data"]["spaces"]:
    #     for strategy in record["strategies"]:
    #         d = strategy["params"]
    #         keys = ['symbol', 'address', "decimals"]
    #         filtered_d = dict((k, d[k]) for k in keys if k in d)
    #         strategy["params"] = filtered_d