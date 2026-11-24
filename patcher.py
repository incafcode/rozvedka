#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rozvedka local patcher.

Takes an already installed, untouched Rozvedka and applies the local crack:
  - account gate -> always active (admin/full)
  - shell always loads the bundled local UI
  - places search/details/classify -> local module (Google key or OSM)
  - remote/server mode disabled in the renderer

Usage:
    python patcher.py                 # patch %USERPROFILE%\\Documents\\Rozvidka\\update
    python patcher.py --dir PATH
    python patcher.py --asar PATH
    python patcher.py --check
    python patcher.py --restore
    python patcher.py --kill          # kill Rozvidka.exe before writing
    python patcher.py --no-backup

No third-party modules. Python 3.8+.
"""

import argparse
import base64
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

RZLOCAL_B64 = "Ly8gTG9jYWwgcmVwbGFjZW1lbnQgZm9yIHRoZSB2ZW5kb3IgR29vZ2xlIFBsYWNlcyBwcm94eS4KLy8gT3JkZXIgb2YgcHJlZmVyZW5jZToKLy8gICAxLiByZWFsIEdvb2dsZSBQbGFjZXMgQVBJIChOZXcpIGtleSAtPiBHb29nbGUKLy8gICAyLiBOb21pbmF0aW0gZnJlZSB0ZXh0IChmYXN0LCB3b3JrcyBmb3IgImNhdGVnb3J5IGluIGNpdHkiKQovLyAgIDMuIE92ZXJwYXNzIGJ5IGNhdGVnb3J5IHRhZ3MgZnJvbSBSWlNwaGVyZXMgKHdoZW4gTm9taW5hdGltIGZpbmRzIHRvbyBsaXR0bGUpCi8vIE5vIGFjY291bnQsIG5vIHZlbmRvciBzZXJ2ZXIuCgpjb25zdCBjYWNoZSA9IG5ldyBNYXAoKTsKY29uc3QgY2l0eUJveENhY2hlID0gbmV3IE1hcCgpOwpjb25zdCBVQV9TVFJJTkcgPSAiUm96dmVka2EvNS4wLjQgKGxvY2FsIGJ1aWxkKSI7CmxldCBub21MYXN0ID0gMDsKbGV0IG92TGFzdCA9IDA7Cgpjb25zdCBzbGVlcCA9IG1zID0+IG5ldyBQcm9taXNlKHIgPT4gc2V0VGltZW91dChyLCBtcykpOwoKZnVuY3Rpb24gcnpTcGhlcmVzKCkgewogIHRyeSB7IHJldHVybiByZXF1aXJlKCIuL3NyYy9zcGhlcmVzLmpzIik7IH0gY2F0Y2ggeyByZXR1cm4gbnVsbDsgfQp9CgovLyAi0LrQsNGE0LUg0LIg0JrQuNC10LLQtSIgLyAiY2FmZSBpbiBLeWl2IiAvICLQutCw0YTQtSwg0JrQuNC10LIiCmZ1bmN0aW9uIHBhcnNlUXVlcnkocSkgewogIGxldCBjYXQgPSBTdHJpbmcocSB8fCAiIikudHJpbSgpOwogIGxldCBjaXR5ID0gIiI7CiAgY29uc3QgbSA9IC9eKC4qPylccysoPzrQsnzRg3xpbilccysoLispJC9pLmV4ZWMoY2F0KTsKICBpZiAobSkgewogICAgY2F0ID0gbVsxXS50cmltKCk7CiAgICBjaXR5ID0gbVsyXS50cmltKCk7CiAgfSBlbHNlIHsKICAgIGNvbnN0IHBhcnRzID0gY2F0LnNwbGl0KCIsIik7CiAgICBpZiAocGFydHMubGVuZ3RoID4gMSkgewogICAgICBjaXR5ID0gcGFydHMucG9wKCkudHJpbSgpOwogICAgICBjYXQgPSBwYXJ0cy5qb2luKCIsIikudHJpbSgpOwogICAgfQogIH0KICByZXR1cm4geyBjYXQsIGNpdHkgfTsKfQoKZnVuY3Rpb24gZXNjUngocykgewogIHJldHVybiBTdHJpbmcocykucmVwbGFjZSgvWy4qKz9eJHt9KCl8W1xdXFxdL2csICJcXCQmIik7Cn0KCi8vIFJaU3BoZXJlcyBzZWxlY3RvcnM6ICJhbWVuaXR5PWNhZmUiLCAiYW1lbml0eT1yZXN0YXVyYW50fGZhc3RfZm9vZDtjdWlzaW5lfnBpenphIgpmdW5jdGlvbiBzZWxUb1FMKHNlbCkgewogIGNvbnN0IGNvbmRzID0gU3RyaW5nKHNlbCB8fCAiIikuc3BsaXQoIjsiKS5tYXAocyA9PiBzLnRyaW0oKSkuZmlsdGVyKEJvb2xlYW4pLm1hcChjID0+IHsKICAgIGNvbnN0IG0gPSAvXihbXHc6XSspKD86KFs9fl0pKC4qKSk/JC8uZXhlYyhjKTsKICAgIGlmICghbSkgcmV0dXJuIG51bGw7CiAgICBjb25zdCBbLCBrLCBvcCwgdl0gPSBtOwogICAgaWYgKCFvcCkgcmV0dXJuICdbIicgKyBrICsgJyJdJzsKICAgIGlmIChvcCA9PT0gIn4iKSByZXR1cm4gJ1siJyArIGsgKyAnIn4iJyArIFN0cmluZyh2KS5yZXBsYWNlKC8iL2csICdcXCInKSArICciLGldJzsKICAgIGlmIChTdHJpbmcodikuaW5jbHVkZXMoInwiKSkgewogICAgICBjb25zdCB2YWxzID0gU3RyaW5nKHYpLnNwbGl0KCJ8IikubWFwKGVzY1J4KTsKICAgICAgcmV0dXJuICdbIicgKyBrICsgJyJ+Il4oJyArIHZhbHMuam9pbigifCIpICsgJykkIl0nOwogICAgfQogICAgcmV0dXJuICdbIicgKyBrICsgJyI9IicgKyBTdHJpbmcodikucmVwbGFjZSgvIi9nLCAnXFwiJykgKyAnIl0nOwogIH0pLmZpbHRlcihCb29sZWFuKTsKICByZXR1cm4gY29uZHMubGVuZ3RoID8gY29uZHMuam9pbigiIikgOiBudWxsOwp9CgpmdW5jdGlvbiBvdmVycGFzc1FMKHNlbGVjdG9ycywgYmJveCkgewogIGNvbnN0IFtzLCBuLCB3LCBlXSA9IGJib3g7CiAgY29uc3QgYm94ID0gW3MsIHcsIG4sIGVdLmpvaW4oIiwiKTsKICBjb25zdCBjbGF1c2VzID0gW107CiAgZm9yIChjb25zdCBzZWwgb2Ygc2VsZWN0b3JzIHx8IFtdKSB7CiAgICBjb25zdCBxbCA9IHNlbFRvUUwoc2VsKTsKICAgIGlmIChxbCkgY2xhdXNlcy5wdXNoKCJud3IiICsgcWwgKyAiKCIgKyBib3ggKyAiKTsiKTsKICB9CiAgaWYgKCFjbGF1c2VzLmxlbmd0aCkgcmV0dXJuIG51bGw7CiAgcmV0dXJuICJbb3V0Ompzb25dW3RpbWVvdXQ6MzBdOygiICsgY2xhdXNlcy5qb2luKCIiKSArICIpO291dCBjZW50ZXIgdGFncyAzMDA7IjsKfQoKYXN5bmMgZnVuY3Rpb24gbm9taW5hdGltKHVybCwgbGFuZykgewogIGNvbnN0IHdhaXQgPSAxMTAwIC0gKERhdGUubm93KCkgLSBub21MYXN0KTsKICBpZiAod2FpdCA+IDApIGF3YWl0IHNsZWVwKHdhaXQpOwogIG5vbUxhc3QgPSBEYXRlLm5vdygpOwogIGNvbnN0IHIgPSBhd2FpdCBmZXRjaCh1cmwsIHsKICAgIGhlYWRlcnM6IHsgIlVzZXItQWdlbnQiOiBVQV9TVFJJTkcsICJBY2NlcHQiOiAiYXBwbGljYXRpb24vanNvbiIgfSwKICAgIHNpZ25hbDogQWJvcnRTaWduYWwudGltZW91dCgzMDAwMCkKICB9KTsKICBpZiAoIXIub2spIHRocm93IG5ldyBFcnJvcigiTm9taW5hdGltICIgKyByLnN0YXR1cyk7CiAgcmV0dXJuIGF3YWl0IHIuanNvbigpOwp9Cgphc3luYyBmdW5jdGlvbiBjaXR5Qm94KGNpdHksIGxhbmcpIHsKICBjb25zdCBrZXkgPSBTdHJpbmcoY2l0eSB8fCAiIikudG9Mb3dlckNhc2UoKTsKICBpZiAoY2l0eUJveENhY2hlLmhhcyhrZXkpKSByZXR1cm4gY2l0eUJveENhY2hlLmdldChrZXkpOwogIGNvbnN0IHBhcmFtcyA9IG5ldyBVUkxTZWFyY2hQYXJhbXMoeyBxOiBjaXR5LCBmb3JtYXQ6ICJqc29udjIiLCBsaW1pdDogIjUiLCBhZGRyZXNzZGV0YWlsczogIjAiIH0pOwogIGlmIChsYW5nKSBwYXJhbXMuc2V0KCJhY2NlcHQtbGFuZ3VhZ2UiLCBTdHJpbmcobGFuZykuc2xpY2UoMCwgNSkpOwogIGxldCBhcnIgPSBbXTsKICB0cnkgewogICAgYXJyID0gYXdhaXQgbm9taW5hdGltKCJodHRwczovL25vbWluYXRpbS5vcGVuc3RyZWV0bWFwLm9yZy9zZWFyY2g/IiArIHBhcmFtcy50b1N0cmluZygpLCBsYW5nKTsKICB9IGNhdGNoIHsKICAgIGNpdHlCb3hDYWNoZS5zZXQoa2V5LCBudWxsKTsKICAgIHJldHVybiBudWxsOwogIH0KICBjb25zdCBsaXN0ID0gQXJyYXkuaXNBcnJheShhcnIpID8gYXJyIDogW107CiAgY29uc3QgcGljayA9IGxpc3QuZmluZCh4ID0+IEFycmF5LmlzQXJyYXkoeC5ib3VuZGluZ2JveCkgJiYKICAgICAgL2NpdHl8dG93bnx2aWxsYWdlfG11bmljaXBhbGl0eXxhZG1pbmlzdHJhdGl2ZS9pLnRlc3QoU3RyaW5nKCh4LmFkZHJlc3N0eXBlIHx8ICIiKSArICIgIiArICh4LnR5cGUgfHwgIiIpKSkpIHx8CiAgICBsaXN0LmZpbmQoeCA9PiBBcnJheS5pc0FycmF5KHguYm91bmRpbmdib3gpKTsKICBjb25zdCBib3ggPSBwaWNrID8gcGljay5ib3VuZGluZ2JveC5tYXAoTnVtYmVyKSA6IG51bGw7CiAgY2l0eUJveENhY2hlLnNldChrZXksIGJveCk7CiAgcmV0dXJuIGJveDsKfQoKYXN5bmMgZnVuY3Rpb24gb3ZlcnBhc3MoYm9keSkgewogIGNvbnN0IHdhaXQgPSAxMTAwIC0gKERhdGUubm93KCkgLSBvdkxhc3QpOwogIGlmICh3YWl0ID4gMCkgYXdhaXQgc2xlZXAod2FpdCk7CiAgb3ZMYXN0ID0gRGF0ZS5ub3coKTsKCiAgY29uc3QgZW5kcG9pbnRzID0gWwogICAgImh0dHBzOi8vb3ZlcnBhc3MtYXBpLmRlL2FwaS9pbnRlcnByZXRlciIsCiAgICAiaHR0cHM6Ly9vdmVycGFzcy5rdW1pLnN5c3RlbXMvYXBpL2ludGVycHJldGVyIgogIF07CiAgbGV0IGxhc3RFcnIgPSBudWxsOwogIGZvciAoY29uc3QgZXAgb2YgZW5kcG9pbnRzKSB7CiAgICB0cnkgewogICAgICBjb25zdCByID0gYXdhaXQgZmV0Y2goZXAsIHsKICAgICAgICBtZXRob2Q6ICJQT1NUIiwKICAgICAgICBoZWFkZXJzOiB7CiAgICAgICAgICAiQ29udGVudC1UeXBlIjogImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIsCiAgICAgICAgICAiVXNlci1BZ2VudCI6IFVBX1NUUklORywKICAgICAgICAgICJBY2NlcHQiOiAiYXBwbGljYXRpb24vanNvbiIKICAgICAgICB9LAogICAgICAgIGJvZHk6ICJkYXRhPSIgKyBlbmNvZGVVUklDb21wb25lbnQoYm9keSksCiAgICAgICAgc2lnbmFsOiBBYm9ydFNpZ25hbC50aW1lb3V0KDQ1MDAwKQogICAgICB9KTsKICAgICAgaWYgKCFyLm9rKSB7CiAgICAgICAgbGFzdEVyciA9IG5ldyBFcnJvcigiT3ZlcnBhc3MgIiArIHIuc3RhdHVzKTsKICAgICAgICBjb250aW51ZTsKICAgICAgfQogICAgICByZXR1cm4gYXdhaXQgci5qc29uKCk7CiAgICB9IGNhdGNoIChlKSB7CiAgICAgIGxhc3RFcnIgPSBlOwogICAgfQogIH0KICB0aHJvdyBsYXN0RXJyIHx8IG5ldyBFcnJvcigiT3ZlcnBhc3MgdW5hdmFpbGFibGUiKTsKfQoKYXN5bmMgZnVuY3Rpb24gb3ZlcnBhc3NTZWFyY2goY2F0LCBjaXR5LCBsYW5nKSB7CiAgY29uc3QgUlogPSByelNwaGVyZXMoKTsKICBjb25zdCBzZWwgPSBSWiAmJiB0eXBlb2YgUloub3NtID09PSAiZnVuY3Rpb24iID8gUloub3NtKGNhdCkgOiBudWxsOwogIGlmICghc2VsIHx8ICFzZWwubGVuZ3RoKSByZXR1cm4gbnVsbDsKCiAgY29uc3QgYm94ID0gYXdhaXQgY2l0eUJveChjaXR5LCBsYW5nKTsKICBpZiAoIWJveCkgcmV0dXJuIG51bGw7CiAgY29uc3QgcWwgPSBvdmVycGFzc1FMKHNlbCwgYm94KTsKICBpZiAoIXFsKSByZXR1cm4gbnVsbDsKCiAgY29uc3QgZGF0YSA9IGF3YWl0IG92ZXJwYXNzKHFsKTsKICBjb25zdCBwbGFjZXMgPSBbXTsKICBmb3IgKGNvbnN0IGVsIG9mIChkYXRhICYmIGRhdGEuZWxlbWVudHMpIHx8IFtdKSB7CiAgICBjb25zdCBwID0gb3ZlcnBhc3NQbGFjZShlbCwgY2l0eSk7CiAgICBpZiAocCkgcGxhY2VzLnB1c2gocCk7CiAgfQogIGNvbnN0IHNlZW4gPSBuZXcgU2V0KCk7CiAgY29uc3QgdW5pcSA9IFtdOwogIGZvciAoY29uc3QgcCBvZiBwbGFjZXMpIHsKICAgIGlmIChzZWVuLmhhcyhwLmlkKSkgY29udGludWU7CiAgICBzZWVuLmFkZChwLmlkKTsKICAgIHVuaXEucHVzaChwKTsKICB9CiAgcmV0dXJuIHVuaXE7Cn0KCmZ1bmN0aW9uIG92ZXJwYXNzUGxhY2UoZWwsIGNpdHkpIHsKICBjb25zdCB0ID0gKGVsICYmIGVsLnRhZ3MgJiYgdHlwZW9mIGVsLnRhZ3MgPT09ICJvYmplY3QiKSA/IGVsLnRhZ3MgOiB7fTsKICBjb25zdCBsYXQgPSBOdW1iZXIoZWwubGF0ICE9IG51bGwgPyBlbC5sYXQgOiBlbC5jZW50ZXIgJiYgZWwuY2VudGVyLmxhdCk7CiAgY29uc3QgbG9uID0gTnVtYmVyKGVsLmxvbiAhPSBudWxsID8gZWwubG9uIDogZWwuY2VudGVyICYmIGVsLmNlbnRlci5sb24pOwogIGlmICghaXNGaW5pdGUobGF0KSB8fCAhaXNGaW5pdGUobG9uKSkgcmV0dXJuIG51bGw7CiAgY29uc3QgbmFtZSA9IHQubmFtZSB8fCB0LmJyYW5kIHx8IHQub3BlcmF0b3IgfHwgIiI7CiAgaWYgKCFuYW1lKSByZXR1cm4gbnVsbDsKCiAgY29uc3Qga2luZCA9IGVsLnR5cGUgPT09ICJub2RlIiA/ICJuIiA6IGVsLnR5cGUgPT09ICJ3YXkiID8gInciIDogInIiOwogIGNvbnN0IGlkID0gKCJvc20iICsga2luZCArIGVsLmlkKS5yZXBsYWNlKC9bXkEtWmEtejAtOV8tXS9nLCAiIikuc2xpY2UoMCwgMjAwKTsKICBjb25zdCBzdHJlZXQgPSBbdFsiYWRkcjpzdHJlZXQiXSwgdFsiYWRkcjpob3VzZW51bWJlciJdXS5maWx0ZXIoQm9vbGVhbikuam9pbigiICIpOwogIGNvbnN0IGFkZHIgPSBbc3RyZWV0LCB0WyJhZGRyOmNpdHkiXSB8fCBjaXR5IHx8ICIiXS5maWx0ZXIoQm9vbGVhbikuam9pbigiLCAiKSB8fCB0WyJhZGRyOmZ1bGwiXSB8fCAiIjsKICBjb25zdCBwcmltYXJ5ID0gdC5hbWVuaXR5IHx8IHQuc2hvcCB8fCB0LmhlYWx0aGNhcmUgfHwgdC50b3VyaXNtIHx8IHQubGVpc3VyZSB8fCB0LmNyYWZ0IHx8IHQub2ZmaWNlIHx8IHQuY3Vpc2luZSB8fCAicGxhY2UiOwoKICBjb25zdCBwbGFjZSA9IHsKICAgIGlkLAogICAgZGlzcGxheU5hbWU6IHsgdGV4dDogbmFtZSwgbGFuZ3VhZ2VDb2RlOiAicnUiIH0sCiAgICBmb3JtYXR0ZWRBZGRyZXNzOiBhZGRyLAogICAgbG9jYXRpb246IHsgbGF0aXR1ZGU6IGxhdCwgbG9uZ2l0dWRlOiBsb24gfSwKICAgIHR5cGVzOiBbdC5hbWVuaXR5LCB0LnNob3AsIHQuaGVhbHRoY2FyZSwgdC50b3VyaXNtLCB0LmxlaXN1cmUsIHQuY3JhZnQsIHQub2ZmaWNlXS5maWx0ZXIoQm9vbGVhbiksCiAgICBwcmltYXJ5VHlwZTogcHJpbWFyeSwKICAgIHByaW1hcnlUeXBlRGlzcGxheU5hbWU6IHsgdGV4dDogcHJpbWFyeSB9LAogICAgd2Vic2l0ZVVyaTogdC53ZWJzaXRlIHx8IHRbImNvbnRhY3Q6d2Vic2l0ZSJdIHx8IHQudXJsIHx8ICIiLAogICAgaW50ZXJuYXRpb25hbFBob25lTnVtYmVyOiB0LnBob25lIHx8IHRbImNvbnRhY3Q6cGhvbmUiXSB8fCAiIiwKICAgIG5hdGlvbmFsUGhvbmVOdW1iZXI6IHQucGhvbmUgfHwgdFsiY29udGFjdDpwaG9uZSJdIHx8ICIiLAogICAgZ29vZ2xlTWFwc1VyaTogImh0dHBzOi8vd3d3Lm9wZW5zdHJlZXRtYXAub3JnLyIgKyBlbC50eXBlICsgIi8iICsgZWwuaWQsCiAgICBidXNpbmVzc1N0YXR1czogIk9QRVJBVElPTkFMIgogIH07CiAgY2FjaGUuc2V0KGlkLCBwbGFjZSk7CiAgcmV0dXJuIHBsYWNlOwp9CgpmdW5jdGlvbiBub21pbmF0aW1QbGFjZShwKSB7CiAgY29uc3QgbGF0ID0gTnVtYmVyKHAgJiYgcC5sYXQpOwogIGNvbnN0IGxvbiA9IE51bWJlcihwICYmIHAubG9uKTsKICBpZiAoIWlzRmluaXRlKGxhdCkgfHwgIWlzRmluaXRlKGxvbikpIHJldHVybiBudWxsOwoKICBjb25zdCBldCA9IChwLmV4dHJhdGFncyAmJiB0eXBlb2YgcC5leHRyYXRhZ3MgPT09ICJvYmplY3QiKSA/IHAuZXh0cmF0YWdzIDoge307CiAgY29uc3QgbmQgPSAocC5uYW1lZGV0YWlscyAmJiB0eXBlb2YgcC5uYW1lZGV0YWlscyA9PT0gIm9iamVjdCIpID8gcC5uYW1lZGV0YWlscyA6IHt9OwogIGNvbnN0IG5hbWUgPSBuZFsibmFtZTpydSJdIHx8IG5kLm5hbWUgfHwgcC5uYW1lIHx8IFN0cmluZyhwLmRpc3BsYXlfbmFtZSB8fCAiIikuc3BsaXQoIiwiKVswXTsKICBjb25zdCBraW5kID0gU3RyaW5nKHAub3NtX3R5cGUgfHwgIngiKS50b0xvd2VyQ2FzZSgpWzBdIHx8ICJ4IjsKICBjb25zdCByYXdJZCA9IFN0cmluZyhwLm9zbV9pZCB8fCAoTWF0aC5yb3VuZChsYXQgKiAxZTUpICsgIiIgKyBNYXRoLnJvdW5kKGxvbiAqIDFlNSkpKTsKICBjb25zdCBpZCA9ICgib3NtIiArIGtpbmQgKyByYXdJZCkucmVwbGFjZSgvW15BLVphLXowLTlfLV0vZywgIiIpLnNsaWNlKDAsIDIwMCk7CgogIGNvbnN0IHBsYWNlID0gewogICAgaWQsCiAgICBkaXNwbGF5TmFtZTogeyB0ZXh0OiBuYW1lIHx8IFN0cmluZyhwLmRpc3BsYXlfbmFtZSB8fCAiIiksIGxhbmd1YWdlQ29kZTogInJ1IiB9LAogICAgZm9ybWF0dGVkQWRkcmVzczogcC5kaXNwbGF5X25hbWUgfHwgIiIsCiAgICBsb2NhdGlvbjogeyBsYXRpdHVkZTogbGF0LCBsb25naXR1ZGU6IGxvbiB9LAogICAgdHlwZXM6IFtwLmNsYXNzLCBwLnR5cGVdLmZpbHRlcihCb29sZWFuKSwKICAgIHByaW1hcnlUeXBlOiBwLnR5cGUgfHwgcC5jbGFzcyB8fCAiIiwKICAgIHByaW1hcnlUeXBlRGlzcGxheU5hbWU6IHsgdGV4dDogcC50eXBlIHx8IHAuY2xhc3MgfHwgIiIgfSwKICAgIHdlYnNpdGVVcmk6IGV0LndlYnNpdGUgfHwgZXRbImNvbnRhY3Q6d2Vic2l0ZSJdIHx8ICIiLAogICAgaW50ZXJuYXRpb25hbFBob25lTnVtYmVyOiBldC5waG9uZSB8fCBldFsiY29udGFjdDpwaG9uZSJdIHx8ICIiLAogICAgbmF0aW9uYWxQaG9uZU51bWJlcjogZXQucGhvbmUgfHwgZXRbImNvbnRhY3Q6cGhvbmUiXSB8fCAiIiwKICAgIGdvb2dsZU1hcHNVcmk6ICJodHRwczovL3d3dy5nb29nbGUuY29tL21hcHMvc2VhcmNoLz9hcGk9MSZxdWVyeT0iICsgbGF0ICsgIiwiICsgbG9uLAogICAgYnVzaW5lc3NTdGF0dXM6ICJPUEVSQVRJT05BTCIKICB9OwoKICBpZiAoQXJyYXkuaXNBcnJheShwLmJvdW5kaW5nYm94KSAmJiBwLmJvdW5kaW5nYm94Lmxlbmd0aCA9PT0gNCkgewogICAgY29uc3QgW3MsIG4sIHcsIGVdID0gcC5ib3VuZGluZ2JveC5tYXAoTnVtYmVyKTsKICAgIGlmIChbcywgbiwgdywgZV0uZXZlcnkoaXNGaW5pdGUpKSB7CiAgICAgIHBsYWNlLnZpZXdwb3J0ID0gewogICAgICAgIGxvdzogeyBsYXRpdHVkZTogcywgbG9uZ2l0dWRlOiB3IH0sCiAgICAgICAgaGlnaDogeyBsYXRpdHVkZTogbiwgbG9uZ2l0dWRlOiBlIH0KICAgICAgfTsKICAgIH0KICB9CiAgY29uc3QgaWcgPSBldFsiY29udGFjdDppbnN0YWdyYW0iXSB8fCBldC5pbnN0YWdyYW07CiAgaWYgKGlnKSBwbGFjZS5faWcgPSBTdHJpbmcoaWcpLnJlcGxhY2UoL15ALywgIiIpOwogIGNhY2hlLnNldChpZCwgcGxhY2UpOwogIHJldHVybiBwbGFjZTsKfQoKYXN5bmMgZnVuY3Rpb24gbm9taW5hdGltU2VhcmNoKHEsIGxhbmcpIHsKICBjb25zdCBwYXJhbXMgPSBuZXcgVVJMU2VhcmNoUGFyYW1zKHsKICAgIHEsIGZvcm1hdDogImpzb252MiIsIGFkZHJlc3NkZXRhaWxzOiAiMSIsIGV4dHJhdGFnczogIjEiLAogICAgbmFtZWRldGFpbHM6ICIxIiwgbGltaXQ6ICI0MCIKICB9KTsKICBpZiAobGFuZykgcGFyYW1zLnNldCgiYWNjZXB0LWxhbmd1YWdlIiwgU3RyaW5nKGxhbmcpLnNsaWNlKDAsIDUpKTsKICBjb25zdCBhcnIgPSBhd2FpdCBub21pbmF0aW0oImh0dHBzOi8vbm9taW5hdGltLm9wZW5zdHJlZXRtYXAub3JnL3NlYXJjaD8iICsgcGFyYW1zLnRvU3RyaW5nKCksIGxhbmcpOwogIHJldHVybiAoQXJyYXkuaXNBcnJheShhcnIpID8gYXJyIDogW10pLm1hcChub21pbmF0aW1QbGFjZSkuZmlsdGVyKEJvb2xlYW4pOwp9Cgphc3luYyBmdW5jdGlvbiBnb29nbGVTZWFyY2goa2V5LCBib2R5LCBtYXNrKSB7CiAgY29uc3QgciA9IGF3YWl0IGZldGNoKCJodHRwczovL3BsYWNlcy5nb29nbGVhcGlzLmNvbS92MS9wbGFjZXM6c2VhcmNoVGV4dCIsIHsKICAgIG1ldGhvZDogIlBPU1QiLAogICAgaGVhZGVyczogewogICAgICAiQ29udGVudC1UeXBlIjogImFwcGxpY2F0aW9uL2pzb24iLAogICAgICAiWC1Hb29nLUFwaS1LZXkiOiBrZXksCiAgICAgICJYLUdvb2ctRmllbGRNYXNrIjogU3RyaW5nKG1hc2sgfHwgInBsYWNlcy5pZCxwbGFjZXMuZGlzcGxheU5hbWUscGxhY2VzLmZvcm1hdHRlZEFkZHJlc3MiKQogICAgfSwKICAgIGJvZHk6IEpTT04uc3RyaW5naWZ5KGJvZHkgfHwge30pLAogICAgc2lnbmFsOiBBYm9ydFNpZ25hbC50aW1lb3V0KDMwMDAwKQogIH0pOwogIGNvbnN0IGpzb24gPSBhd2FpdCByLmpzb24oKS5jYXRjaCgoKSA9PiBudWxsKTsKICBpZiAoci5vaykgewogICAgZm9yIChjb25zdCBwIG9mIChqc29uICYmIGpzb24ucGxhY2VzKSB8fCBbXSkgaWYgKHAgJiYgcC5pZCkgY2FjaGUuc2V0KFN0cmluZyhwLmlkKSwgcCk7CiAgICByZXR1cm4geyBvazogdHJ1ZSwgc3RhdHVzOiAyMDAsIGpzb24sIHRleHQ6IG51bGwgfTsKICB9CiAgcmV0dXJuIHsKICAgIG9rOiBmYWxzZSwgc3RhdHVzOiByLnN0YXR1cywganNvbiwKICAgIHRleHQ6IChqc29uICYmIGpzb24uZXJyb3IgJiYganNvbi5lcnJvci5tZXNzYWdlKSB8fCAoIkdvb2dsZSAiICsgci5zdGF0dXMpCiAgfTsKfQoKYXN5bmMgZnVuY3Rpb24gc2VhcmNoKGFwaUtleSwgYm9keSwgbWFzaykgewogIHRyeSB7CiAgICBjb25zdCBrZXkgPSBTdHJpbmcoYXBpS2V5IHx8ICIiKTsKICAgIGlmICgvXkFJemFbMC05QS1aYS16Xy1dezIwLH0kLy50ZXN0KGtleSkpIHsKICAgICAgY29uc3QgZyA9IGF3YWl0IGdvb2dsZVNlYXJjaChrZXksIGJvZHksIG1hc2spOwogICAgICBpZiAoZy5vaykgcmV0dXJuIGc7CiAgICAgIC8vIGludmFsaWQga2V5IC8gcXVvdGEgLyBiaWxsaW5nOiBjb250aW51ZSB3aXRoIE9TTQogICAgfQoKICAgIGNvbnN0IHEgPSBTdHJpbmcoKGJvZHkgJiYgKGJvZHkudGV4dFF1ZXJ5IHx8IGJvZHkucXVlcnkpKSB8fCAiIikudHJpbSgpOwogICAgaWYgKCFxKSByZXR1cm4geyBvazogZmFsc2UsIHN0YXR1czogNDAwLCBqc29uOiBudWxsLCB0ZXh0OiAiZW1wdHkgcXVlcnkiIH07CiAgICBjb25zdCBsYW5nID0gYm9keSAmJiBib2R5Lmxhbmd1YWdlQ29kZTsKICAgIGNvbnN0IHsgY2F0LCBjaXR5IH0gPSBwYXJzZVF1ZXJ5KHEpOwoKICAgIGxldCBwbGFjZXMgPSBbXTsKICAgIHRyeSB7CiAgICAgIHBsYWNlcyA9IGF3YWl0IG5vbWluYXRpbVNlYXJjaChxLCBsYW5nKTsKICAgIH0gY2F0Y2gge30KCiAgICBpZiAocGxhY2VzLmxlbmd0aCA8IDUgJiYgY2l0eSkgewogICAgICB0cnkgewogICAgICAgIGNvbnN0IGV4dHJhID0gYXdhaXQgb3ZlcnBhc3NTZWFyY2goY2F0LCBjaXR5LCBsYW5nKTsKICAgICAgICBpZiAoZXh0cmEgJiYgZXh0cmEubGVuZ3RoKSB7CiAgICAgICAgICBjb25zdCBzZWVuID0gbmV3IFNldChwbGFjZXMubWFwKHAgPT4gcC5pZCkpOwogICAgICAgICAgZm9yIChjb25zdCBwIG9mIGV4dHJhKSBpZiAoIXNlZW4uaGFzKHAuaWQpKSB7IHNlZW4uYWRkKHAuaWQpOyBwbGFjZXMucHVzaChwKTsgfQogICAgICAgIH0KICAgICAgfSBjYXRjaCB7fQogICAgfQoKICAgIHJldHVybiB7IG9rOiB0cnVlLCBzdGF0dXM6IDIwMCwganNvbjogeyBwbGFjZXMgfSwgdGV4dDogcGxhY2VzLmxlbmd0aCA/IG51bGwgOiAibm8gcmVzdWx0cyIgfTsKICB9IGNhdGNoIChlKSB7CiAgICByZXR1cm4geyBvazogZmFsc2UsIHN0YXR1czogMCwganNvbjogbnVsbCwgdGV4dDogU3RyaW5nKChlICYmIGUubWVzc2FnZSkgfHwgZSkgfTsKICB9Cn0KCmFzeW5jIGZ1bmN0aW9uIGRldGFpbHMoYXBpS2V5LCBpZCwgbWFzaywgbGFuZykgewogIGNvbnN0IGtleSA9IFN0cmluZyhpZCB8fCAiIik7CiAgY29uc3QgaGl0ID0gY2FjaGUuZ2V0KGtleSk7CiAgaWYgKGhpdCkgcmV0dXJuIHsgb2s6IHRydWUsIHN0YXR1czogMjAwLCBqc29uOiBoaXQsIHRleHQ6IG51bGwgfTsKCiAgaWYgKC9eQUl6YVswLTlBLVphLXpfLV17MjAsfSQvLnRlc3QoU3RyaW5nKGFwaUtleSB8fCAiIikpKSB7CiAgICB0cnkgewogICAgICBjb25zdCB1ID0gImh0dHBzOi8vcGxhY2VzLmdvb2dsZWFwaXMuY29tL3YxL3BsYWNlcy8iICsgZW5jb2RlVVJJQ29tcG9uZW50KGtleSkgKwogICAgICAgIChsYW5nID8gIj9sYW5ndWFnZUNvZGU9IiArIGVuY29kZVVSSUNvbXBvbmVudChsYW5nKSA6ICIiKTsKICAgICAgY29uc3QgciA9IGF3YWl0IGZldGNoKHUsIHsKICAgICAgICBoZWFkZXJzOiB7ICJYLUdvb2ctQXBpLUtleSI6IGFwaUtleSwgIlgtR29vZy1GaWVsZE1hc2siOiBTdHJpbmcobWFzayB8fCAiKiIpIH0sCiAgICAgICAgc2lnbmFsOiBBYm9ydFNpZ25hbC50aW1lb3V0KDIwMDAwKQogICAgICB9KTsKICAgICAgY29uc3QganNvbiA9IGF3YWl0IHIuanNvbigpLmNhdGNoKCgpID0+IG51bGwpOwogICAgICBpZiAoci5vaykgcmV0dXJuIHsgb2s6IHRydWUsIHN0YXR1czogMjAwLCBqc29uLCB0ZXh0OiBudWxsIH07CiAgICAgIHJldHVybiB7CiAgICAgICAgb2s6IGZhbHNlLCBzdGF0dXM6IHIuc3RhdHVzLCBqc29uLAogICAgICAgIHRleHQ6IChqc29uICYmIGpzb24uZXJyb3IgJiYganNvbi5lcnJvci5tZXNzYWdlKSB8fCAoIkdvb2dsZSAiICsgci5zdGF0dXMpCiAgICAgIH07CiAgICB9IGNhdGNoIChlKSB7CiAgICAgIHJldHVybiB7IG9rOiBmYWxzZSwgc3RhdHVzOiAwLCBqc29uOiBudWxsLCB0ZXh0OiBTdHJpbmcoKGUgJiYgZS5tZXNzYWdlKSB8fCBlKSB9OwogICAgfQogIH0KCiAgY29uc3QgbSA9IC9eb3NtKFtud3JdKShcZCspJC8uZXhlYyhrZXkpOwogIGlmIChtKSB7CiAgICB0cnkgewogICAgICBjb25zdCB0eXBlID0geyBuOiAiTiIsIHc6ICJXIiwgcjogIlIiIH1bbVsxXV07CiAgICAgIGNvbnN0IHUgPSAiaHR0cHM6Ly9ub21pbmF0aW0ub3BlbnN0cmVldG1hcC5vcmcvZGV0YWlscz9vc210eXBlPSIgKyB0eXBlICsKICAgICAgICAiJm9zbWlkPSIgKyBtWzJdICsgIiZmb3JtYXQ9anNvbiZhZGRyZXNzZGV0YWlscz0xJmV4dHJhdGFncz0xJmhpZXJhcmNoeT0wIjsKICAgICAgY29uc3QgaiA9IGF3YWl0IG5vbWluYXRpbSh1LCBsYW5nKTsKICAgICAgY29uc3QgYyA9IGogJiYgai5jZW50cm9pZCAmJiBqLmNlbnRyb2lkLmNvb3JkaW5hdGVzOwogICAgICBjb25zdCBwID0gewogICAgICAgIG9zbV90eXBlOiB0eXBlLAogICAgICAgIG9zbV9pZDogbVsyXSwKICAgICAgICBsYXQ6IGMgPyBjWzFdIDogdW5kZWZpbmVkLAogICAgICAgIGxvbjogYyA/IGNbMF0gOiB1bmRlZmluZWQsCiAgICAgICAgZGlzcGxheV9uYW1lOiAoaiAmJiBqLmxvY2FsbmFtZSkgfHwgIiIsCiAgICAgICAgbmFtZTogKGogJiYgai5uYW1lcyAmJiAoai5uYW1lc1sibmFtZTpydSJdIHx8IGoubmFtZXMubmFtZSkpIHx8IChqICYmIGoubG9jYWxuYW1lKSB8fCAiIiwKICAgICAgICBleHRyYXRhZ3M6IChqICYmIGouZXh0cmF0YWdzKSB8fCB7fSwKICAgICAgICBjbGFzczogKGogJiYgai50eXBlKSB8fCAiIiwKICAgICAgICB0eXBlOiAoaiAmJiBqLmNhdGVnb3J5KSB8fCAiIgogICAgICB9OwogICAgICBjb25zdCBwbGFjZSA9IG5vbWluYXRpbVBsYWNlKHApOwogICAgICBpZiAocGxhY2UpIHJldHVybiB7IG9rOiB0cnVlLCBzdGF0dXM6IDIwMCwganNvbjogcGxhY2UsIHRleHQ6IG51bGwgfTsKICAgIH0gY2F0Y2gge30KICAgIHJldHVybiB7IG9rOiBmYWxzZSwgc3RhdHVzOiA0MDQsIGpzb246IG51bGwsIHRleHQ6ICJub3QgZm91bmQiIH07CiAgfQoKICByZXR1cm4geyBvazogZmFsc2UsIHN0YXR1czogNDA0LCBqc29uOiBudWxsLCB0ZXh0OiAibm90IGZvdW5kIiB9Owp9CgpmdW5jdGlvbiBjbGFzc2lmeShzaXRlcykgewogIGNvbnN0IGFyciA9IEFycmF5LmlzQXJyYXkoc2l0ZXMpID8gc2l0ZXMgOiBbXTsKICByZXR1cm4geyBvazogdHJ1ZSwgcnVsZXNWZXJzaW9uOiAibG9jYWwtMSIsIHJlc3VsdHM6IGFyci5tYXAoKCkgPT4gIndhcm0iKSB9Owp9Cgptb2R1bGUuZXhwb3J0cyA9IHsgc2VhcmNoLCBkZXRhaWxzLCBjbGFzc2lmeSB9Owo="

PATCHED_ACCESS = 'function access(){return{ok:!0,state:"in"}}'
PATCHED_PAIDOK = "function paidOk(e,t){return!0}"
STATUS_INSERT = ('return{enabled:!0,state:"in",note:"",bot:"",google:!1,email:!1,'
                 'pass:!1,mailOtp:!1,hasSess:!0,version:version,user:{id:"local",'
                 'email:"",name:"local",region:"",price:"",role:"admin",status:"active",'
                 'edition:"full",paid_ok:!0,paid_until:null,trial_until:null,devices:[]}};')

HANDLER_CLASSIFY = ('ipcMain.handle("places:classify",async(e,t)=>{try{return '
                    'require("./rzlocal").classify(t&&t.sites,t&&t.markers)}catch(e){'
                    'return{ok:!1,error:String(e&&e.message||e)}}}),')
HANDLER_SEARCH = ('ipcMain.handle("places:search",async(e,t)=>{try{return await '
                  'require("./rzlocal").search(t&&t.apiKey,t&&t.body,t&&t.fieldMask)}'
                  'catch(e){return{ok:!1,status:0,json:null,text:String(e&&e.message||e)}}});')
HANDLER_DETAILS = ('ipcMain.handle("places:details",async(e,t)=>{const n=t&&t.id;'
                   'if("string"!=typeof n||!/^[A-Za-z0-9_-]{8,300}$/.test(n))'
                   'return{ok:!1,status:0,json:null,text:"bad id"};try{return await '
                   'require("./rzlocal").details(t&&t.apiKey,n,t.fieldMask,t.lang)}'
                   'catch(e){return{ok:!1,status:0,json:null,text:String(e&&e.message||e)}}}),')

DEFAULT_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents" / "Rozvidka" / "update"


class PatchError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# ASAR (read / pack)
# ---------------------------------------------------------------------------

def read_asar(path):
    data = Path(path).read_bytes()
    if len(data) < 16:
        raise PatchError("file too small to be an ASAR")
    a, header_total = struct.unpack_from("<II", data, 0)
    payload_size, json_len = struct.unpack_from("<II", data, 8)
    if a != 4:
        raise PatchError("not an ASAR (bad prefix)")
    if payload_size + 4 != header_total or header_total < json_len + 8:
        raise PatchError("corrupt ASAR header")
    header = json.loads(data[16:16 + json_len].decode("utf-8"))
    data_start = 8 + header_total
    blob = data[data_start:]
    return header, blob


def walk_entries(node, prefix=""):
    for name, ent in node.get("files", {}).items():
        path = name if not prefix else prefix + "/" + name
        if "files" in ent:
            yield from walk_entries(ent, path)
        else:
            yield path, ent


def extract_files(header, blob):
    files = {}
    for path, ent in walk_entries(header):
        if ent.get("unpacked"):
            raise PatchError("unpacked ASAR entries are not supported: " + path)
        off = int(ent["offset"])
        size = int(ent["size"])
        files[path] = blob[off:off + size]
    return files


def pack_asar(header, files):
    # update sizes/offsets, drop old integrity metadata, preserve executable flags
    offset = 0
    order = []
    existing = set()
    for path, ent in walk_entries(header):
        existing.add(path)
        content = files[path]
        ent["size"] = len(content)
        ent["offset"] = str(offset)
        ent.pop("integrity", None)
        order.append((path, content))
        offset += len(content)

    # add new root files that are not in the tree yet
    for path, content in files.items():
        if path in existing:
            continue
        if "/" in path:
            raise PatchError("new nested files are not supported: " + path)
        header["files"][path] = {"size": len(content), "offset": str(offset)}
        order.append((path, content))
        offset += len(content)

    json_bytes = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    pad = (-len(json_bytes)) % 4
    padded = json_bytes + b"\0" * pad
    header_total = 8 + len(padded)
    payload_size = 4 + len(padded)

    out = bytearray()
    out += struct.pack("<IIII", 4, header_total, payload_size, len(json_bytes))
    out += padded
    for _, content in order:
        out += content
    return bytes(out)


# ---------------------------------------------------------------------------
# Patch helpers
# ---------------------------------------------------------------------------

def replace_between(src, start_marker, end_marker, new_text):
    i = src.find(start_marker)
    if i < 0:
        raise PatchError("start marker not found: " + start_marker[:60])
    j = src.find(end_marker, i + len(start_marker))
    if j < 0:
        raise PatchError("end marker not found after " + start_marker[:60])
    return src[:i] + new_text + src[j:]


def cut_function(src, start_marker, end_markers, new_text):
    i = src.find(start_marker)
    if i < 0:
        raise PatchError("function not found: " + start_marker)
    end = None
    for marker in end_markers:
        k = src.find(marker, i + len(start_marker))
        if k >= 0 and (end is None or k < end):
            end = k
    if end is None:
        raise PatchError("end of function not found: " + start_marker)
    return src[:i] + new_text + src[end:]


def patch_account(src):
    if "function access(){" not in src:
        raise PatchError("account.js: access() not found")

    if "function access(){return{ok:!0,state:\"in\"}}" not in src:
        src = cut_function(src, "function access(){",
                           ["function paidOk", "function status"], PATCHED_ACCESS)

    if "function paidOk(" not in src:
        raise PatchError("account.js: paidOk() not found")
    if "function paidOk(e,t){return!0}" not in src:
        src = cut_function(src, "function paidOk(",
                           ["function status", "function access"], PATCHED_PAIDOK)

    marker = "function status(){"
    i = src.find(marker)
    if i < 0:
        raise PatchError("account.js: status() not found")
    if STATUS_INSERT not in src[:i + len(marker) + 40]:
        src = src[:i + len(marker)] + STATUS_INSERT + src[i + len(marker):]
    return src


def patch_rzshell(src):
    if "function localFlag(){" not in src:
        raise PatchError("rzshell.js: localFlag() not found")
    if "function localFlag(){return!0}" in src:
        return src
    return cut_function(src, "function localFlag(){",
                        ["const web=", "const web ="], "function localFlag(){return!0}")


def patch_app_main(src):
    src = replace_between(src, 'ipcMain.handle("places:classify"',
                          'ipcMain.handle("places:search"', HANDLER_CLASSIFY)
    src = replace_between(src, 'ipcMain.handle("places:search"',
                          'const csvName=', HANDLER_SEARCH)
    src = replace_between(src, 'ipcMain.handle("places:details"',
                          'ipcMain.handle("gis2:search"', HANDLER_DETAILS)
    return src


def patch_core(src):
    if "function gRemote(){return!0}" in src:
        src = src.replace("function gRemote(){return!0}", "function gRemote(){return false}", 1)
    elif "function gRemote(){return false}" not in src:
        raise PatchError("core.js: gRemote() not found")

    old = 'let apiKey=gRemote()?GK_SRV:LS.get("apiKey","")'
    if old in src:
        src = src.replace(old, 'let apiKey=LS.get("apiKey","")||"local"', 1)
    elif 'let apiKey=LS.get("apiKey","")||"local"' not in src:
        raise PatchError("core.js: apiKey default not found")

    # fresh installs should start on Google/OSM, not on 2GIS which needs a server key
    if 'DEFAULTS={cities:' in src:
        src = src.replace('DEFAULTS={cities:', 'DEFAULTS={source:"google",cities:', 1)
    elif 'DEFAULTS={source:"google",cities:' not in src:
        raise PatchError("core.js: DEFAULTS not found")
    return src


def patch_app_js(src):
    old = 'apiKey=await migrate("apiKey","google"),gRemote()&&(apiKey=GK_SRV)'
    new = 'apiKey=await migrate("apiKey","google")||"local"'
    if old in src:
        src = src.replace(old, new, 1)
    elif new not in src:
        raise PatchError("app.js: apiKey migration not found")

    old2 = '$("apiKey").value=gRemote()?"":apiKey'
    new2 = '$("apiKey").value=gRemote()||"local"===apiKey?"":apiKey'
    if old2 in src:
        src = src.replace(old2, new2, 1)
    elif new2 not in src:
        raise PatchError("app.js: apiKey field not found")
    return src


def verify(files):
    checks = {
        "account.js": ['function access(){return{ok:!0,state:"in"}}',
                       "function paidOk(e,t){return!0}",
                       'state:"in"'],
        "rzshell.js": ["function localFlag(){return!0}"],
        "app-main.js": ['require("./rzlocal")'] * 3,
        "src/core.js": ["function gRemote(){return false}",
                        'let apiKey=LS.get("apiKey","")||"local"',
                        'DEFAULTS={source:"google",cities:'],
        "src/app.js": ['apiKey=await migrate("apiKey","google")||"local"'],
        "rzlocal.js": ["module.exports"],
    }
    for name, needles in checks.items():
        text = files[name].decode("utf-8", "replace")
        for needle in needles:
            if needle not in text:
                raise PatchError("verification failed: %s missing %s" % (name, needle[:60]))


# ---------------------------------------------------------------------------
# App / filesystem helpers
# ---------------------------------------------------------------------------

def find_asar(update_dir):
    update_dir = Path(update_dir)
    if not update_dir.is_dir():
        raise PatchError("update directory not found: " + str(update_dir))
    version = None
    vj = update_dir / "version.json"
    if vj.exists():
        try:
            version = str(json.loads(vj.read_text("utf-8-sig")).get("version") or "")
        except Exception:
            pass
    if version:
        candidate = update_dir / ("app-%s.asar" % version)
        if candidate.exists():
            return candidate
    candidates = sorted(update_dir.glob("app-*.asar"),
                        key=lambda p: [int(x) if x.isdigit() else 0 for x in p.stem.split("-")[-1].split(".")])
    if not candidates:
        raise PatchError("no app-*.asar in " + str(update_dir))
    return candidates[-1]


def running():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Rozvidka.exe"],
                             capture_output=True, text=True, timeout=15,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return "Rozvidka.exe" in (out.stdout or "")
    except Exception:
        return False


def ensure_not_running(kill):
    if not running():
        return
    if kill:
        subprocess.run(["taskkill", "/IM", "Rozvidka.exe", "/F"],
                       capture_output=True, timeout=20,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return
    raise PatchError("Rozvedka.exe is running - close it or pass --kill")


def write_atomic(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    try:
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def patch(asar_path, backup=True, kill=False):
    asar_path = Path(asar_path)
    ensure_not_running(kill)

    header, blob = read_asar(asar_path)
    files = extract_files(header, blob)

    for required in ("account.js", "rzshell.js", "app-main.js", "src/core.js", "src/app.js"):
        if required not in files:
            raise PatchError("unexpected archive layout: missing " + required)

    files["account.js"] = patch_account(files["account.js"].decode("utf-8")).encode("utf-8")
    files["rzshell.js"] = patch_rzshell(files["rzshell.js"].decode("utf-8")).encode("utf-8")
    files["app-main.js"] = patch_app_main(files["app-main.js"].decode("utf-8")).encode("utf-8")
    files["src/core.js"] = patch_core(files["src/core.js"].decode("utf-8")).encode("utf-8")
    files["src/app.js"] = patch_app_js(files["src/app.js"].decode("utf-8")).encode("utf-8")
    files["rzlocal.js"] = base64.b64decode(RZLOCAL_B64).decode("utf-8").encode("utf-8")

    verify(files)

    out = pack_asar(header, files)

    bak = asar_path.with_name(asar_path.name + ".orig")
    if backup and not bak.exists():
        shutil.copy2(asar_path, bak)
        print("[+] backup: %s" % bak)
    elif backup:
        print("[*] backup already exists: %s" % bak)

    write_atomic(asar_path, out)
    print("[+] patched: %s (%d bytes)" % (asar_path, len(out)))
    print("[+] done. Start Rozvedka normally.")


def check(asar_path):
    header, blob = read_asar(asar_path)
    files = extract_files(header, blob)
    verify(files)
    print("[+] patch markers OK in %s" % asar_path)


def restore(asar_path):
    asar_path = Path(asar_path)
    bak = asar_path.with_name(asar_path.name + ".orig")
    if not bak.exists():
        raise PatchError("backup not found: " + str(bak))
    ensure_not_running(False)
    shutil.copy2(bak, asar_path)
    print("[+] restored: %s" % asar_path)


def main():
    ap = argparse.ArgumentParser(description="Local patcher for an installed Rozvedka")
    ap.add_argument("--dir", help="update directory (default: %%USERPROFILE%%\\Documents\\Rozvidka\\update)")
    ap.add_argument("--asar", help="path to app-<version>.asar (overrides --dir)")
    ap.add_argument("--check", action="store_true", help="only verify an already patched archive")
    ap.add_argument("--restore", action="store_true", help="restore the .orig backup")
    ap.add_argument("--kill", action="store_true", help="kill Rozvedka.exe before writing")
    ap.add_argument("--no-backup", action="store_true", help="do not create a .orig backup")
    args = ap.parse_args()

    try:
        if args.asar:
            asar_path = Path(args.asar)
        else:
            asar_path = find_asar(args.dir or DEFAULT_DIR)
        print("[*] archive: %s" % asar_path)

        if args.check:
            check(asar_path)
        elif args.restore:
            restore(asar_path)
        else:
            patch(asar_path, backup=not args.no_backup, kill=args.kill)
        return 0
    except PatchError as e:
        print("[!] %s" % e, file=sys.stderr)
        return 1
    except PermissionError as e:
        print("[!] access denied: %s (close Rozvedka or run as admin)" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
