package org.sunbird.analytics.util

import java.sql.{ResultSet, Statement}

import io.zonky.test.db.postgres.embedded.EmbeddedPostgres
import java.sql.Connection

object EmbeddedPostgresql {

  var pg: EmbeddedPostgres = null;
  var connection: Connection = null;
  var stmt: Statement = null;

  def start() {
    pg = EmbeddedPostgres.builder().setPort(65124).start()
    connection = pg.getPostgresDatabase().getConnection()
    stmt = connection.createStatement()
  }

  def createNominationTable(): Boolean = {
    val tableName: String = "nomination"
    val query = s"""
                   |CREATE TABLE IF NOT EXISTS $tableName (
                   |    program_id TEXT PRIMARY KEY,
                   |    status TEXT)""".stripMargin

    execute(query)
  }

  def createProgramTable(): Boolean = {
    val tableName: String = "program"
    val query = s"""
                   |CREATE TABLE IF NOT EXISTS $tableName (
                   |    program_id TEXT PRIMARY KEY,
                   |    name TEXT,
                   |    enddate TEXT,
                   |    rootorg_id TEXT,
                   |    channel TEXT,
                   |    status TEXT,
                   |    startdate TEXT)""".stripMargin

    execute(query)
  }

  def execute(sqlString: String): Boolean = {
    stmt.execute(sqlString)
  }

  def executeQuery(sqlString: String): ResultSet = {
    stmt.executeQuery(sqlString)
  }

  def dropTable(tableName: String): Boolean = {
    stmt.execute(s"DROP TABLE $tableName")
  }

  def close() {
    stmt.close()
    connection.close()
    pg.close()
  }
}
