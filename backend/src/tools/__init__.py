from .calendar_tool import get_upcoming_events, create_calendar_event
from .search_tool import web_search
from .sql_tool import query_business_database

TOOLS = [get_upcoming_events, create_calendar_event, web_search, query_business_database]