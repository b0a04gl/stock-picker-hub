import pickle

import pandas
import redis

import async_reader


class DataService:
    def __init__(self, redis_host, redis_port, redis_db):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)

    def store_data(self, data):

        data_serialized = pickle.dumps(data)
        self.r.set('my_dataframe', data_serialized)

    def retrieve_data(self):

        data_serialized = self.r.get('past_week_stock_data')
        if data_serialized is not None:
            print("retrieved from redis")
            return pickle.loads(data_serialized)
        else:
            print("cache miss, downloading")
            return async_reader.get_stock_data()

    def store_screen(self, data):
        conditions_df = pandas.DataFrame(data)
        serialized_df = pickle.dumps(conditions_df)

        auto_incremented_id = self.r.incr('auto_increment_id')
        redis_key = f'conditions_df:{auto_incremented_id}'
        self.r.set(redis_key, serialized_df)
        return auto_incremented_id

    def retrieve_screener(self, screener_id):
        retrieved_key = f'conditions_df:{screener_id}'

        conditions_df = self.r.get(retrieved_key)
        if conditions_df:
            return pickle.loads(conditions_df).to_dict(orient='records')

    def retrieve_data_for_screener(self, screener_id):
        conditions = self.retrieve_screener(screener_id)
        print("screener conditions retrieved ..")

        df = self.retrieve_data()
        print("data stock data retrieved .. ")
        return self.apply_conditions(df, conditions)

    @staticmethod
    def apply_conditions(df, conditions):
        for condition in conditions:
            indicator_name = condition['indicator_name']
            operation = condition['operation']
            value = float(condition['value'])
            print("condition to apply : ", condition)
            if operation == ">":
                df = df[df[indicator_name] > value]
            elif operation == "<":
                df = df[df[indicator_name] < value]
            elif operation == "==":
                df = df[df[indicator_name] == value]

        return df

    def retrieve_screeners(self):
        latest_id = int(self.r.get('auto_increment_id') or 0)
        map_entries = []

        for i in range(1, latest_id + 1):
            redis_key = f'conditions_df:{i}'

            serialized_df = self.r.get(redis_key)
            if serialized_df:
                retrieved_df = pickle.loads(serialized_df)
                map_entries.append(retrieved_df)

        if map_entries:

            combined_df = pandas.concat(map_entries, ignore_index=True)

            combined_df.reset_index(drop=True, inplace=True)

            return combined_df
        else:
            return None
