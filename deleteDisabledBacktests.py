from mysql.connector import connect
import DataManagement.Database.StrategyTable as StrategyTable
import DataManagement.Database.BacktestTable as BacktestTable
import CredentialsConfig.server_auth_config as db_auth_config

if __name__ == '__main__':
    with connect(
            host=db_auth_config.host,
            user=db_auth_config.userDB,
            password=db_auth_config.passwordDB,
            database=db_auth_config.database
        ) as connection, connection.cursor() as cursor:
        toDelete = StrategyTable.getDisabledStrategyIds(cursor)
        count = 1
        length = len(toDelete)
        lengthStr = str(length)
        for id in toDelete:
            if count % 200 == 0 or count == length:
                print("progress: " + str(count) + "/" + lengthStr)
            BacktestTable.deleteByStrategyId(cursor, id[0])
            count += 1
        connection.commit()