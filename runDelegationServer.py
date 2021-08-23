import Backtesting.DelegationNetwork.DelegationServer as DelegationServer
import CredentialsConfig.server_auth_config as db_auth_config
from mysql.connector import connect, Error 

if __name__ == '__main__':
    try:
        with connect(
            host=db_auth_config.host,
            user=db_auth_config.userDB,
            password=db_auth_config.passwordDB,
            database=db_auth_config.database
        ) as connection:
            with connection.cursor() as cursor:
                DelegationServer.runDelegationServer(connection, cursor)

    except Error as e:
        print("error with db: ", e)