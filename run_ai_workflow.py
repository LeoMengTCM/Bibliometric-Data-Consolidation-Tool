#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""向后兼容的工作流入口。"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bibliometrics.pipeline.workflow import main


if __name__ == '__main__':
    main()
