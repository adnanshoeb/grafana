# FreeSWITCH Monitoring Dashboard

This repository contains a Grafana dashboard for monitoring FreeSWITCH instances using metrics from the `freeswitch_exporter`. The dashboard provides insights into FreeSWITCH performance, status, and operational metrics.

## Overview

The `FreeSWITCH Monitoring` dashboard (`freeswitch-monitoring-v3.json`) visualizes key metrics for FreeSWITCH, a scalable open-source telephony platform. It leverages Prometheus as the datasource to collect metrics exposed by the `freeswitch_exporter`.

### Dashboard Details
- **Version**: 3
- **UID**: MnCMBZVVz
- **Schema Version**: Grafana 41
- **Datasource**: Prometheus (`beqlfso2jdjpcf`)
- **Metrics Covered**:
  - System Status: `freeswitch_up`, `freeswitch_uptime_seconds`, `freeswitch_current_idle_cpu`
  - Session Metrics: `freeswitch_max_sessions`, `freeswitch_max_sps`, `freeswitch_registrations`, `freeswitch_sessions_total`, `freeswitch_current_sessions`, `freeswitch_current_sessions_peak`, `freeswitch_current_sessions_peak_last_5min`, `freeswitch_current_sps`, `freeswitch_current_sps_peak_last_5min`
  - Gateway Metrics: `freeswitch_sofia_gateway_status`, `freeswitch_sofia_gateway_ping`, `freeswitch_sofia_gateway_call_in`, `freeswitch_sofia_gateway_call_out`, `freeswitch_sofia_gateway_failed_call_in`, `freeswitch_sofia_gateway_failed_call_out`
  - Module and Codec Status: `freeswitch_load_module`, `freeswitch_codec_status`
  - Endpoint and Call Metrics: `freeswitch_endpoint_status`, `freeswitch_current_calls`, `freeswitch_bridged_calls`, `freeswitch_detailed_calls`
- **Features**:
  - Collapsible rows for better organization
  - Modernized visualizations with `stat`, `gauge`, and `timeseries` panels
  - Dynamic thresholds and color-coded alerts
  - Templating for instance selection
  - Time range set to last 6 hours by default, with 30-second refresh

## Installation

### Prerequisites
- **Grafana**: Version 10.0 or higher (compatible with schema version 41)
- **Prometheus**: Configured as a datasource in Grafana
- **freeswitch_exporter**: Running and exposing metrics to Prometheus (see [freeswitch_exporter setup](#freeswitch-exporter-setup))
