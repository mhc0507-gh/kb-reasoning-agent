sample_documents = [
"""
Title: Connection Rejected Diagnostic
Steps:
    1. Check connection response code.
    2. If error code, issue is indicated by the error code.
""",
"""
Title: High link latency diagnostic
Steps:
    1. Check link status.
    2. If disconnected, issue is caused by bad link state.
    3. If connected, check current system load.
    4. Also check system load 5 minutes ago.
    5. If both are above 90% then system is overloaded.
""",
"""
Title: Connection Failure Diagnostic
Steps:
    1. Check link status.
    2. If disconnected, issue is caused by bad link state.
""",
"""
Title: Origin service {service-id} with high latency on more than 90% of requests in the last hour
Steps:
    1. Get percentage of requests with high latency for {service-id} in the last hour
    2. If percentage of requests with high latency is less than 90% then report root cause as "alert error"
    3. Get average end-to-end latency for {service-id} requests in the last hour
    4. Get average server latency for {service-id} requests in the last hour
    5a. If server latency is less than 10% of end-to-end latency then report root cause as "high latency caused by external factors"
    5b. If storage latency is more than 50% of end-to-end latency then report root cause as "high latency caused by storage"
    6. Get {deployment-id} where {service-id} is running
    7. Get average CPU load of {deployment-id} in the last hour
    8. If CPU load is above 90% then go to "High CPU usage in {deployment-id} diagnostic" KB article
    9. Otherwise report root cause as "unable to determine cause of high latency"
""",
"""
Title: High CPU usage in {deployment-id} diagnostic
Steps:
    1. Get average number of requests per second for {deployment-id} in the last hour
    2. Get number of role instances for {deployment-id}
    3. If number of requests per second per role instance is greater than 100 then report root cause as "system overloaded with too many requests"
    4. Otherwise report root cause as "unable to determine cause of high CPU usage"
"""
]