# Taja.bot
슬랙에서 타자연습 게임을 할 수 있습니다.  Play typing practice games in Slack.

<img width="758" alt="sample" src="https://github.com/munggo/Taja.bot/assets/2849747/245fe3a7-315c-4ada-9eb8-697c55dabbe6">


### Slack App Configureation https://app.slack.com/
1. Connect using Socket Mode Change to **Enable Socket Mode**
2. Event Subscriptions > **Subscribe to bot events**
  * app_metion
  * message.channel
  * message.groups
  * message.im
  * message.mpim
3. OAuth & Permissions > **Scopes**
  * app_mentions:read
  * channels:history
  * channels:join
  * channels:read
  * chat:write
  * commands
  * groups:history
  * groups:read
  * im:history
  * im:read
  * im:write
  * mpim:history
  * mpim:read
  * users.profile:read
  * users:read
