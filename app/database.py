from cassandra.cluster import Cluster
import json
import time

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        with open('conf.json', 'r') as f:
            data = json.load(f)
        
        self.host = data['cassandra']['host']
        self.port = data['cassandra']['port']
        self.keyspace = "my_keyspace"
        self.session = self._get_session()
        self._initialized = True

    def _get_session(self):
        while True:
            try:
                cluster = Cluster([self.host], port=self.port)
                session = cluster.connect()
                print("Connected to Cassandra!")
                break
            except Exception as e:
                print(f"Connection failed: {e}. Retrying...")
                time.sleep(5)

        try:
            session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
                WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
            """)
        except Exception as e:
            print(f"Ошибка при создании keyspace: {e}")

        session.set_keyspace(self.keyspace)
        self._create_tables(session)
        return session

    def _create_tables(self, session):
        session.execute("""
            CREATE TABLE IF NOT EXISTS computers (
                serial_number text PRIMARY KEY,
                brand text,
                department_number int
            )
        """)

        session.execute("""
            CREATE TABLE IF NOT EXISTS configurations (
                brand text,
                department_number int,
                num_terminals int,
                num_storage_devices int,
                PRIMARY KEY (brand, department_number)
            )
        """)

# Создаем единственный экземпляр базы данных
db = Database()
session = db.session 