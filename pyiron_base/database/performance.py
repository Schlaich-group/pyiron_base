import pandas as pd
from sqlalchemy import (
    create_engine,
    select,
    distinct,
    MetaData,
    Table,
    func,
    or_,
    false,
)
from pyiron_base.settings.generic import Settings


__author__ = "Muhammad Hassani"
__copyright__ = (
    "Copyright 2020, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Muhammad Hassani"
__email__ = "hassani@mpie.de"


class DatabaseStatistics:
    def __init__(self):
        s = Settings()
        self._connection_string = s._configuration['sql_connection_string']
        self._job_table = s._configuration['sql_table_name']
        if "postgresql" not in self._connection_string:
            raise RuntimeError(
                """
                The detabase statistics is only available for a Postgresql database
                """
            )
        self._table = s._configuration['sql_table_name']
        self._engine = create_engine(self._connection_string)
        self._performance_dict = {}
        self.total_index_size = 0
        self._metadata = MetaData()
        self._stat_view = Table('pg_stat_activity', self._metadata, autoload_with=self._engine)
        self._locks_view = Table('pg_locks', self._metadata, autoload_with=self._engine)

    def _num_conn(self, conn):
        """
        return the number of connections
        """
        stmt = select(func.count()).select_from(self._stat_view)
        result = conn.execute(stmt)
        self._performance_dict['total num. connection'] = result.fetchone()[0]

    def _num_conn_by_state(self, conn):
        """
        return the number of connection, categorized by their state:
        active, idle, idle in transaction, idle in transaction (aborted)
        """
        stmt = select(self._stat_view.c.state, func.count()).\
            select_from(self._stat_view).group_by(self._stat_view.c.state)
        results = conn.execute(stmt).fetchall()
        for result in results:
            key = 'Number of ' + str(result[0]) + ' connection'
            val = int(result[1])
            self._performance_dict[key] = val

    def _num_conn_waiting_locks(self, conn):
        """
        returns the number of connection waiting for locks
        """
        stmt = select(func.count(distinct(self._locks_view.c.pid))).where(self._locks_view.c.granted == false())
        self._performance_dict['num. of conn. waiting for locks'] = \
            conn.execute(stmt).fetchone()[0]

    def _max_trans_age(self, conn):
        """
        returns the maximum age of a transaction
        """
        stmt = select(func.max(func.now() - self._stat_view.c.xact_start)).select_from(self._stat_view).where(
            or_(self._stat_view.c.state == 'idle in transaction', self._stat_view.c.state == 'active'))
        self._performance_dict['max. transaction age'] = str(conn.execute(stmt).fetchone()[0])

    def _index_size(self, conn):
        """
        returns the total size of indexes for the pyiron job table (defined in the
        pyiron_base.Setting._configuration)
        """
        stmt = """
            SELECT
                t.schemaname,
                t.tablename,
                c.reltuples::bigint                            AS num_rows,
                pg_size_pretty(pg_relation_size(c.oid))        AS table_size,
                psai.indexrelname                              AS index_name,
                pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
                CASE WHEN i.indisunique THEN 'Y' ELSE 'N' END  AS "unique",
                psai.idx_scan                                  AS number_of_scans,
                psai.idx_tup_read                              AS tuples_read,
                psai.idx_tup_fetch                             AS tuples_fetched
            FROM
                pg_tables t
                LEFT JOIN pg_class c ON t.tablename = c.relname
                LEFT JOIN pg_index i ON c.oid = i.indrelid
                LEFT JOIN pg_stat_all_indexes psai ON i.indexrelid = psai.indexrelid
            WHERE
                t.schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY 1, 2;        
            """
        rows = conn.execute(stmt).fetchall()
        self._index_usage = 0
        for row in rows:
            if row[1] == self._job_table:
                self._index_usage = self._index_usage + int(str(row[5]).split(' ')[0])

        self._performance_dict['index size/usage (MB)'] = self._index_usage

    def _duplicate_indices(self, conn):
        """
        returns the duplicates in indices
        """
        stmt = """
            SELECT pg_size_pretty(sum(pg_relation_size(idx))::bigint) as size,
                       (array_agg(idx))[1] as idx1, (array_agg(idx))[2] as idx2,
                       (array_agg(idx))[3] as idx3, (array_agg(idx))[4] as idx4
                FROM (
                    SELECT indexrelid::regclass as idx, 
                        (indrelid::text ||E'\n'|| indclass::text ||E'\n'|| indkey::text ||E'\n'||
                        coalesce(indexprs::text,'')||E'\n' || coalesce(indpred::text,'')) as key
                    FROM pg_index) sub
                GROUP BY key HAVING count(*)>1
                ORDER BY sum(pg_relation_size(idx)) DESC;
        """
        overlapping_indices = conn.execute(stmt).fetchall()
        self._performance_dict['duplicated indices'] = ''
        for pair in overlapping_indices:
            self._performance_dict['duplicated indices'] = str(pair[1]) + \
                                                        ', and ' + str(pair[2]) + 'with total size: ' \
                                                        + str(pair[0]) + '\n'

    def _checkpoints_interval(self, conn):
        """
        returns the number of checkpoints and their intervals
        """
        stmt = """
        SELECT
            total_checkpoints,
            seconds_since_start / total_checkpoints / 60 AS minutes_between_checkpoints
            FROM
            (SELECT
            EXTRACT(EPOCH FROM (now() - pg_postmaster_start_time())) AS seconds_since_start,
            (checkpoints_timed+checkpoints_req) AS total_checkpoints
            FROM pg_stat_bgwriter
            ) AS sub;
        """
        check_points = conn.execute(stmt).fetchone()
        self._performance_dict['num. checkpoints'] = check_points[0]
        self._performance_dict['checkpoint interval'] = check_points[1]

    def performance(self):
        """
        returns a pandas dataframe with the essential statistics of a pyiron postgres database
        """
        with self._engine.connect() as conn:
            self._num_conn(conn)
            self._num_conn_by_state(conn)
            self._num_conn_waiting_locks(conn)
            self._max_trans_age(conn)
            self._checkpoints_interval(conn)
            self._index_size(conn)
            self._duplicate_indices(conn)

        return pd.dataframe(self._performance_dict, index=['performance'])
