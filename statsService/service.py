import grpc
import stats_pb2
import stats_pb2_grpc
from concurrent import futures
import clickhouse_connect

client = clickhouse_connect.get_client(host='clickhouse')

class StatsService(stats_pb2_grpc.StatsServiceServicer):
    def GetTaskStats(self, request, context):
        likes_query = client.query('SELECT count FROM (SELECT task_id, count() as count FROM (SELECT DISTINCT user_id, task_id FROM stats.main WHERE type=\'LIKE\') GROUP BY task_id) WHERE task_id=' + str(request.taskId)).result_rows
        likes = 0
        if len(likes_query) > 0:
            likes = likes_query[0][0]
        views_query = client.query('SELECT count FROM (SELECT task_id, count() as count FROM (SELECT DISTINCT user_id, task_id FROM stats.main WHERE type=\'VIEW\') GROUP BY task_id) WHERE task_id=' + str(request.taskId)).result_rows
        views = 0
        if len(views_query) > 0:
            views = views_query[0][0]

        task_stats = stats_pb2.TaskStats(
            id=request.taskId,
            likes=likes,
            views=views,
        )

        return stats_pb2.TaskStatsReply(
            taskStats=task_stats
        )

    def GetTopTasks(self, request, context):
        if request.isLikes:
            query = client.query('SELECT task_id, count FROM (SELECT task_id, count() as count FROM (SELECT DISTINCT user_id, task_id FROM stats.main WHERE type=\'LIKE\') GROUP BY task_id) ORDER BY count DESC LIMIT 5').result_rows
        else:
            query = client.query('SELECT task_id, count FROM (SELECT task_id, count() as count FROM (SELECT DISTINCT user_id, task_id FROM stats.main WHERE type=\'VIEW\') GROUP BY task_id) ORDER BY count DESC LIMIT 5').result_rows

        result = stats_pb2.TopTasksStatsReply()
        for row in query:
            result.tasks.add(
                id=row[0],
                stat=row[1]
            )

        return result

    def GetTopUsers(self, request, context):
        query = client.query('SELECT author, count FROM (SELECT author, count() as count FROM (SELECT DISTINCT user_id, task_id, author FROM stats.authors) GROUP BY author) ORDER BY count DESC LIMIT 3').result_rows

        result = stats_pb2.TopUsersReply()
        for row in query:
            result.users.add(
                login=row[0],
                likes=row[1]
            )

        return result

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stats_pb2_grpc.add_StatsServiceServicer_to_server(StatsService(), server)
    server.add_insecure_port('[::]:5011')
    server.start()
    server.wait_for_termination()