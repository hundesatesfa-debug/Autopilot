package com.example

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.engine.RuleEngine
import com.example.model.ActionCategory
import com.example.model.AgentRequest
import com.example.model.DecisionOutcome
import com.example.model.RiskLevel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class ExampleRobolectricTest {

  @Test
  fun `read string from context`() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val appName = context.getString(R.string.app_name)
    assertEquals("AutoPilot AI", appName)
  }

  @Test
  fun `balanced profile approves safe test command`() {
    val req = AgentRequest(
      id = "req_1",
      agentId = "claude_code",
      agentName = "Claude Code",
      category = ActionCategory.TEST_RUN,
      actionDescription = "Run tests",
      command = "npm test"
    )
    val res = RuleEngine.evaluate(req, RuleEngine.defaultBalancedProfile)
    assertEquals(DecisionOutcome.APPROVED, res.outcome)
    assertTrue(res.autoApproved)
  }

  @Test
  fun `balanced profile blocks destructive delete command`() {
    val req = AgentRequest(
      id = "req_2",
      agentId = "cursor",
      agentName = "Cursor",
      category = ActionCategory.FILE_DELETE,
      actionDescription = "Purge files",
      command = "rm -rf /"
    )
    val res = RuleEngine.evaluate(req, RuleEngine.defaultBalancedProfile)
    assertEquals(DecisionOutcome.DENIED, res.outcome)
    assertFalse(res.autoApproved)
    assertEquals(RiskLevel.CRITICAL, res.riskLevel)
  }

  @Test
  fun `manual profile holds actions pending`() {
    val req = AgentRequest(
      id = "req_3",
      agentId = "claude_code",
      agentName = "Claude Code",
      category = ActionCategory.TEST_RUN,
      actionDescription = "Run tests",
      command = "npm test"
    )
    val res = RuleEngine.evaluate(req, RuleEngine.defaultManualProfile)
    assertEquals(DecisionOutcome.PENDING, res.outcome)
    assertFalse(res.autoApproved)
  }
}
