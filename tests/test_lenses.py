import unittest
from lenses_python.lenses import lenses


class TestLenses(unittest.TestCase):
    def setUp(self):
        self.conn = lenses("http://localhost:3030", "admin", "admin")

    def test_GetCredentials(self):
        recv = {'user': {'name': 'Lenses Admin', 'roles': ['admin', 'write', 'read', 'nodata'],
                         'email': None, 'id': 'admin'}}
        self.assertEqual(self.conn.GetCredentials()['user'], recv['user'])

    def test_SqlHandler(self):
        recv = {'messages': [{'value': '{"VendorID":2,"tpep_pickup_datetime":"2016-01-01 00:00:00",'
                                       '"tpep_dropoff_datetime":"2016-01-01 00:00:00","passenger_count":2,'
                                       '"trip_distance":1.1,"pickup_longitude":-73.99037170410156,'
                                       '"pickup_latitude":40.73469543457031,"RateCodeID":1,"store_and_fwd_flag":"N",'
                                       '"dropoff_longitude":-73.98184204101562,"dropoff_latitude":40.73240661621094,'
                                       '"payment_type":2,"fare_amount":7.5,"extra":0.5,"mta_tax":0.5,'
                                       '"improvement_surcharge":0.3,"tip_amount":0.0,"tolls_amount":0.0,'
                                       '"total_amount":8.8}', 'key': None, 'timestamp': 1525255998747,
                              'topic': 'nyc_yellow_taxi_trip_data', 'partition': 0, 'offset': 0}], 'offset': []}
        query = "SELECT * FROM `nyc_yellow_taxi_trip_data` WHERE _vtype='AVRO' AND _ktype='BYTES' AND _sample=2 " \
                "AND _sampleWindow=200 limit 1"
        self.assertEqual(self.conn.SqlHandler(query)["messages"][0]["value"], recv["messages"][0]["value"])

    def test_GetAllTopics(self):
        recv = {'topicName': '_kafka_lenses_lsql_storage'}
        self.assertEqual(self.conn.GetAllTopics()[0]['topicName'], recv['topicName'])

    def test_TopicInfo(self):
        topic_name = '_kafka_lenses_lsql_storage'
        recv = {'topicName': '_kafka_lenses_lsql_storage'}
        self.assertEqual(self.conn.TopicInfo(topic_name)['topicName'], recv['topicName'])

    def test_TopicsNames(self):
        if len(list(self.conn.TopicsNames())) < 1:
            raise AssertionError('Unexpected raise exception,no topic names retrieve')

    def test_UpdateTopicConfig(self):
        config = {"configs": [{"key": "cleanup.policy", "value": "compact"}]
                  }
        try:
            self.conn.UpdateTopicConfig('_kafka_lenses_lsql_storage', config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_CreateTopic(self):
        config = {
            "cleanup.policy": "compact",
            "compression.type": "snappy"
            }
        try:
            self.conn.CreateTopic("test_topic", 1, 1, config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteTopic(self):
        try:
            self.conn.DeleteTopic("test_topic")
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_CreateProcessor(self):
        query = " SET autocreate=true; insert into body SELECT  body FROM  `reddit_posts` WHERE score> 10 and _" \
                "ktype=AVRO and _vtype=AVRO "
        self.assertEqual(self.conn.CreateProcessor("test_processor", query, 1, 'dev', 'ns', '1').split('_')[0], 'lsql')

    def test_DeleteProcessor(self):
        query = " SET autocreate=true; insert into body SELECT  body FROM  `reddit_posts` WHERE score> 10 and _" \
                "ktype=AVRO and _vtype=AVRO "
        try:
            processor_id = self.conn.CreateProcessor("test_processor_2", query, 1, 'dev', 'ns', '1')
            self.conn.DeleteProcessor(processor_id)
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_ResumeProcessor(self):
        query = " SET autocreate=true; insert into body SELECT  body FROM  `reddit_posts` WHERE score> 10 and _" \
                "ktype=AVRO and _vtype=AVRO "
        try:
            processor_id = self.conn.CreateProcessor("test_processor_3", query, 1, 'dev', 'ns', '1')
            self.conn.ResumeProcessor(processor_id)
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_PauseProcessor(self):
        query = " SET autocreate=true; insert into body SELECT  body FROM  `reddit_posts` WHERE score> 10 and _" \
                "ktype=AVRO and _vtype=AVRO "
        try:
            processor_id = self.conn.CreateProcessor("test_processor_4", query, 1, 'dev', 'ns', '1')
            self.conn.PauseProcessor(processor_id)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_UpdateProcessorRunners(self):
        query = " SET autocreate=true; insert into body SELECT  body FROM  `reddit_posts` WHERE score> 10 and _" \
                "ktype=AVRO and _vtype=AVRO "
        try:
            processor_id = self.conn.CreateProcessor("test_processor_5", query, 1, 'dev', 'ns', '1')
            self.conn.UpdateProcessorRunners(processor_id, '4')
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_GetAllSubjects(self):
        if len(list(self.conn.GetAllSubjects())) < 1:
            raise AssertionError('Unexcepted raise exception, no subjects retrieve')

    def test_ListVersionsSubj(self):
        subj = self.conn.GetAllSubjects()[0]
        if len(list(self.conn.ListVersionsSubj(subj))) < 0:
            raise AssertionError('Unexcepted raise exception, no version of subject has retrieve')

    def test_GetSchemaById(self):
        schema = {'schema': '{"type":"record","name":"reddit_post_key",'
                            '"namespace":"com.landoop.social.reddit.post.key",'
                            '"fields":[{"name":"testit_id","type":"string"}]}'
                  }
        schema_id = str(self.conn.RegisterNewSchema("test_schema", schema)['id'])
        self.assertEqual(list(self.conn.GetSchemaById(schema_id).keys())[0], 'schema')

    def test_GetSchemaByVer(self):
        subj = self.conn.GetAllSubjects()[0]
        if type(self.conn.GetSchemaByVer(subj, '1')) != type({}):
            raise AssertionError('Unexcepted raise exception, no version of subject has retrieve')

    def test_RegisterNewSchema(self):
        schema = {'schema': '{"type":"record","name":"reddit_post_key",'
                            '"namespace":"com.landoop.social.reddit.post.key",'
                            '"fields":[{"name":"subreddit_id","type":"string"}]}'
                  }
        self.assertEqual(list(self.conn.RegisterNewSchema("test", schema).keys())[0], 'id')

    def test_GetGlobalCompatibility(self):
        recv = {'compatibilityLevel': 'BACKWARD'}
        self.assertEqual(self.conn.GetGlobalCompatibility(), recv)

    # def test_GetCompatibility(self):
    #     # conn = lenses("http://localhost:3030", "admin", "admin")
    #     try:
    #         subj = self.conn.GetAllSubjects()[0]
    #         self.assertEqual(list(self.conn.GetCompatibility(subj).keys())[0],'compatibilityLevel')
    #     except Exception as e:
    #         raise AssertionError('Unexcepted raise exception, no version of subject has retrieve')

    def test_DeleteSubj(self):
        try:
            subj = self.conn.GetAllSubjects()[0]
            self.conn.DeleteSubj(subj)
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_DeleteSchemaByVersion(self):
        subj = "cc_payments-value"
        try:
            self.conn.DeleteSchemaByVersion(subj, '1')
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_ChangeCompatibility(self):
        config = {'compatibility': 'BACKWARD'}
        subj = "cc_payments-value"
        try:
            self.conn.ChangeCompatibility(subj, config)
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_UpdateGlobalCompatibility(self):
        config = {'compatibility': 'BACKWARD'}
        try:
            self.conn.UpdateGlobalCompatibility(config)
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_ListAllConnectors(self):
        recv = ['logs-broker', 'nullsink']
        self.assertEqual(self.conn.ListAllConnectors('dev'), recv)

    def test_GetInfoConnector(self):
        recv = {'name': 'logs-broker', 'tasks': [{'connector': 'logs-broker', 'task': 0}],
                'config': {'file': '/var/log/broker.log', 'name': 'logs-broker', 'topic': 'logs_broker',
                           'connector.class': 'org.apache.kafka.connect.file.FileStreamSourceConnector',
                           'tasks.max': '1'}, 'type': 'source'}
        self.assertEqual(self.conn.GetInfoConnector('dev', 'logs-broker'), recv)

    def test_GetConnectorConfig(self):
        recv = {'file': '/var/log/broker.log', 'name': 'logs-broker', 'topic': 'logs_broker',
                'connector.class': 'org.apache.kafka.connect.file.FileStreamSourceConnector', 'tasks.max': '1'}
        self.assertEqual(self.conn.GetConnectorConfig('dev', 'logs-broker'), recv)

    def test_GetConnectorStatus(self):
        recv = {'name': 'logs-broker', 'tasks': [{'state': 'RUNNING', 'worker_id': '172.17.0.2:8083', 'id': 0}],
                'connector': {'state': 'RUNNING', 'worker_id': '172.17.0.2:8083'}, 'type': 'source'}
        self.assertEqual(self.conn.GetConnectorStatus('dev', 'logs-broker')['name'], 'logs-broker')

    def test_GetConnectorTasks(self):
        recv = [{'config': {'file': '/var/log/broker.log',
                            'task.class': 'org.apache.kafka.connect.file.FileStreamSourceTask', 'topic': 'logs_broker'},
                 'id': {'connector': 'logs-broker', 'task': 0}}]
        self.assertEqual(self.conn.GetConnectorTasks('dev', 'logs-broker'), recv)

    def test_GetStatusTask(self):
        recv = {'state': 'RUNNING', 'worker_id': '172.17.0.2:8083', 'id': 0}
        self.assertEqual(self.conn.GetStatusTask('dev', 'logs-broker', '0')['state'], 'RUNNING')

    def test_RestartConnectorTask(self):
        try:
            self.conn.RestartConnector('dev', 'logs-broker')
        except Exception as e:
            raise AssertionError('Unexcepted raise exception:', e)

    def test_GetConnectorPlugins(self):
        recv = {'name': 'Couchbase', 'class': 'com.couchbase.connect.kafka.CouchbaseSinkConnector',
                'icon': 'couchbase.png', 'type': 'sink', 'description': 'Write Kafka data to Couchbase',
                'version': '3.2.2', 'author': 'Couchbase',
                'docs': '//developer.couchbase.com/documentation/server/current/connectors/kafka-3.1/quickstart.html',
                'uiEnabled': True}
        self.assertEqual(self.conn.GetConnectorPlugins('dev')[0], recv)

    def test_PauseConnector(self):
        try:
            self.conn.RestartConnector('dev', 'logs-broker')
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_ResumeConnector(self):
        try:
            self.conn.ResumeConnector('dev', 'logs-broker')
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_RestartConnector(self):
        try:
            self.conn.RestartConnector('dev', 'logs-broker')
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_CreateConnector(self):
        config = {'config': {'connect.coap.kcql': '1',
                             'connector.class':
                                 'com.datamountaineer.streamreactor.connect.coap.sink.CoapSinkConnector'},
                  'name': 'test_connector'
                  }
        recv = {'config':

                    {'connect.coap.kcql': '1',
                     'connector.class': 'com.datamountaineer.streamreactor.connect.coap.sink.CoapSinkConnector',
                     'name': 'test_connector'
                     },
                'tasks': [], 'type': None, 'name': 'test_connector'
                }
        self.assertEqual(self.conn.CreateConnector('dev', config), recv)

    def test_SetConnectorConfig(self):
        config = {'connector.class': 'org.apache.kafka.connect.file.FileStreamSinkConnector',
                            'task.max': 5,
                            'topics': 'nyc_yellow_taxi_trip_data,reddit_posts,sea_vessel_position_reports,telecom_italia_data',
                            'file': '/dev/null',
                            'tasks.max': '4',
                            'name': 'nullsink'}
        try:
            self.conn.SetConnectorConfig('dev', 'nullsink', config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteConnector(self):
        try:
            self.conn.DeleteConnector('dev', 'test_connector')
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_GetACLs(self):
        self.assertEqual(self.conn.GetACLs(), [])

    def test_SetACL(self):
        try:
            self.conn.SetACL("Topic", "transactions", "GROUPA:UserA", "Allow", "*", "Read")
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_GetQuotas(self):
        self.assertEqual(self.conn.GetQuotas(), [])

    def test_SetQuotasAllUsers(self):
        config = {"producer_byte_rate": "100000",
                  "consumer_byte_rate": "200000",
                  "request_percentage": "75"
                  }
        try:
            self.conn.SetQuotasAllUsers(config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_SetQuotaUserAllClients(self):
        config = {"producer_byte_rate": "100000",
                  "consumer_byte_rate": "200000",
                  "request_percentage": "75"
                  }
        try:
            self.conn.SetQuotasAllUsers(config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_SetQuotaUserClient(self):
        config = {"producer_byte_rate": "100000",
                  "consumer_byte_rate": "200000",
                  "request_percentage": "75"
                  }
        try:
            self.conn.SetQuotaUserClient('admin', 'admin', config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_SetQuotaUser(self):
        config = {"producer_byte_rate": "100000",
                  "consumer_byte_rate": "200000",
                  "request_percentage": "75"
                  }
        try:
            self.conn.SetQuotaUser("admin", config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_SetQuotaAllClient(self):
        config = {"producer_byte_rate": "100000",
                  "consumer_byte_rate": "200000",
                  "request_percentage": "75"
                  }
        try:
            self.conn.SetQuotaAllClient(config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_SetQuotaClient(self):
        config = {"producer_byte_rate": "100000",
                  "consumer_byte_rate": "200000",
                  "request_percentage": "75"
                  }
        try:
            self.conn.SetQuotaClient("admin", config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteQutaAllUsers(self):
        config = ['consumer_byte_rate', 'producer_byte_rate', 'request_percentage']
        try:
            self.conn.DeleteQutaAllUsers(config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteQuotaUserAllClients(self):
        config = ['consumer_byte_rate', 'producer_byte_rate', 'request_percentage']
        try:
            self.conn.DeleteQuotaUserAllClients("admin", config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteQuotaUserClient(self):
        config = ['consumer_byte_rate', 'producer_byte_rate', 'request_percentage']
        try:
            self.conn.DeleteQuotaUserClient("admin", "admin", config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteQuotaUser(self):
        config = ['consumer_byte_rate', 'producer_byte_rate', 'request_percentage']
        try:
            self.conn.DeleteQuotaUser("admin", config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteQuotaAllClients(self):
        config = ['consumer_byte_rate', 'producer_byte_rate', 'request_percentage']
        try:
            self.conn.DeleteQuotaAllClients(config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)

    def test_DeleteQuotaClient(self):
        config = ['consumer_byte_rate', 'producer_byte_rate', 'request_percentage']
        try:
            self.conn.DeleteQuotaClient('admin', config)
        except Exception as e:
            raise AssertionError('Unexpected raise exception:', e)


if __name__ == '__main__':
    unittest.main()



