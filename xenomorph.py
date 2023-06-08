NAME = 'xenomorph'

DICT_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] - %(levelname)s: %(message).10000s [in %(pathname)s:%(lineno)d]',
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'xenomorph.log',
            'formatter': 'standard',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'root': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
