#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# imports
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import update

Base = declarative_base()