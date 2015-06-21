# -*- coding: utf-8 -*-

EMAIL_ENCODING = 'iso-2022-jp'

MSG_DEBUG = u"デバッグ"
MSG_INFO = u"情報"
MSG_WARN = u"警戒"
MSG_ERROR = u"危険"
MSG_CRITICAL = u"緊急"

MSG_PROC_NOT_RUNNING = u'起動していません'
MSG_PROC_RUNNING = u'%(count)d 個 起動しています'
MSG_PROC_STATUS_FORMAT = u'[%(level)s] %(name)s: %(count)s ("%(condition)s" に違反)'
MSG_PROC_ALERT_TITLE = u'プロセス異常を検知しました'
MSG_PROC_ALERT = u'サーバ %(server_id)s にて、以下のプロセス異常を検知しました。\n\n%(result)s\n\n以上'

MSG_SUBJECT_FORMAT = u'【%(level)s】[%(group_id)s:%(server_id)s] %(title)s (%(start_time)s)'
