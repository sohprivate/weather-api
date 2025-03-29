from graphs.weather_graph import build_weather_graph

graph = build_weather_graph()
result = graph.invoke({})

print("\n=== LangGraph結果 ===")
print(result["final_decision"])