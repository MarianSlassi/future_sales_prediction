Methods:
- extract()
- full_schema()
- month_aggregations()
- first_month()
- expanding_window()
- year_month()
- was_in_test()
- downcast_dtype()
- lags()
- deltas()
- output()




Functions: 
- size_memmory_info()


Syntax:
Every method represents a heading from notebook. Every sub heading devvided by two \n. Every cell devided by one \n

Architecture:
Better to store variables locally across methods and keep instnce variables of object as much clean as possible, since we have big enough dataframe for memmory malloc or overflow. Some operations provided with function syntax of the file to import in case of need (probable will remove them to helper.py)