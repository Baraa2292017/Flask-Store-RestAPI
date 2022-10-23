"""
Simple methodology to save  expired tokens

Better approach is to use DB to store expired tokens, Redis for example
"""

expired_tokens = set()
