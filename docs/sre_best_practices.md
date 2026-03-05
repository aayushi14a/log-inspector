# Intuit SRE Best Practices & Runbook

## 1. Payment Service Failures (PAY_TIMEOUT_*, PAY_FAIL_*)

### Immediate Actions
- Check Stripe status page: https://status.stripe.com
- Verify network connectivity to Stripe API from payment-service pods
- If Stripe is down: enable fallback payment processor (PayPal backup)
- Increase retry timeout from 30s to 60s during degraded periods

### Long-Term Fixes
- Implement circuit breaker pattern (Hystrix/Resilience4j) with 50% failure threshold
- Add a secondary payment gateway (Adyen or PayPal) as automatic failover
- Set up synthetic monitoring for Stripe API latency (alert at p99 > 5s)
- Add payment queue (Kafka) so transactions aren't lost during outages

---

## 2. Out of Memory Errors (DOC_OOM_*, Java Heap)

### Immediate Actions
- Restart affected pods immediately
- Increase JVM heap: -Xmx from 2G to 4G on doc-service
- Check for memory leaks: run jmap heap dump on next occurrence

### Long-Term Fixes
- Switch PDF rendering to streaming mode (don't load full doc in memory)
- Implement resource limits per request (max 50MB per PDF)
- Set up JVM memory alerts at 80% threshold
- Consider moving to a non-JVM PDF renderer (e.g., WeasyPrint, Puppeteer)

---

## 3. Database Issues (DB_REPL_*, DB_FAILOVER_*)

### Immediate Actions
- Verify replication lag: `SHOW SLAVE STATUS` on replica
- If lag > 30s: redirect read traffic to primary temporarily
- Check for long-running queries blocking replication

### Long-Term Fixes
- Implement read replicas with health-aware load balancing
- Set up automated failover with < 500ms switchover (ProxySQL or PgBouncer)
- Add replication lag monitoring with PagerDuty alert at 10s threshold
- Consider moving to a multi-region active-active setup

---

## 4. SSL Certificate Failures (SSL_CERT_*)

### Immediate Actions
- Check certificate expiry: `openssl s_client -connect <host>:443`
- If expired: rotate certificate immediately via cert-manager
- Verify intermediate CA chain is complete

### Long-Term Fixes
- Automate cert rotation with cert-manager + Let's Encrypt
- Set up certificate expiry alerts at 30-day and 7-day thresholds
- Implement mTLS for all service-to-service communication
- Add certificate monitoring dashboard

---

## 5. Security Incidents (SEC_BRUTE_*, SEC_DDOS_*, BILL_SEC_*)

### Immediate Actions
- For brute force: verify account lock is active, notify user via email
- For DDoS: confirm WAF rules are applied, check if legitimate traffic is blocked
- For webhook attacks: rotate Stripe webhook signing secret immediately

### Long-Term Fixes
- Implement progressive rate limiting (10/min → 5/min → block)
- Add CAPTCHA after 3 failed login attempts
- Set up DDoS mitigation with Cloudflare or AWS Shield
- Implement webhook signature verification with timestamp validation (reject > 5min old)
- Add anomaly detection ML model for traffic pattern analysis

---

## 6. ETL Pipeline Failures (ETL_FAIL_*, ETL_SCHEMA_*)

### Immediate Actions
- Check source data schema for changes
- Run manual reconciliation for affected date partition
- Notify downstream consumers of data delay

### Long-Term Fixes
- Implement schema registry (Apache Avro) for all data contracts
- Add schema validation step before transform stage
- Set up data quality checks (Great Expectations)
- Implement dead letter queue for failed records instead of failing entire job

---

## 7. Slow Queries & Performance (DB_SLOW_*, RPT_LARGE_*)

### Immediate Actions
- Identify the slow query: check pg_stat_statements or slow query log
- Add missing indexes if obvious (e.g., user_profiles.user_id)
- For large reports: add pagination or async generation

### Long-Term Fixes
- Implement query timeout at 5s for user-facing requests
- Add read replicas for reporting workloads
- Cache frequently accessed data (Redis, 5-min TTL)
- Move large report generation to async job queue (Celery/SQS)

---

## General Best Practices

1. **Circuit Breakers**: All external API calls must have circuit breakers (open at 50% failures over 1-min window)
2. **Retry Policy**: Max 3 retries with exponential backoff (1s, 2s, 4s)
3. **Timeouts**: All HTTP calls must have connect timeout (5s) and read timeout (30s)
4. **Logging**: Always include request_id, user_id, and error_code in log entries
5. **Alerting**: CRITICAL = PagerDuty immediate, ERROR = Slack alert, WARN = dashboard only
6. **Disk Space**: Alert at 85%, auto-cleanup at 90%, page SRE at 95%
7. **Health Checks**: All services must expose /healthz with dependency checks
8. **Graceful Degradation**: Every service must have a fallback mode
