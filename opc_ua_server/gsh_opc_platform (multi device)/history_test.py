from datetime import datetime, timedelta
week_test = datetime.today().month

print(week_test)

"""
            try:
                last_known_timestamp = previous_data.iloc[0]['SourceTimestamp']
                last_known_timestamp = datetime.strptime(last_known_timestamp, '%Y-%m-%d %H:%M:%S.%f')
                previous_month = last_known_timestamp.month
            except:
                previous_ww = datetime.today().isocalendar()[1]
            if previous_ww != datetime.today().isocalendar()[1]:
                initial_value = 0
                crsr.execute(f"DELETE FROM '{value[0]}_{value[1]}';")
                self.server_logger_signal.emit(('log',"Executing database cleanup!"))
            else:"""