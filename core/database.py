#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# imports
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import update

Base = declarative_base()

class targets(Base):
    	__tablename__ = "targets"

	id            = Column(Integer, primary_key=True)
	address       = Column(String(50), nullable=False)
	os_match      = Column(Text, nullable=True)
	os_accuracy   = Column(Text, nullable=True)
	ipv4          = Column(String(50), nullable=True)
	ipv6          = Column(String(250), nullable=True)
	mac           = Column(String(50), nullable=True)
	status        = Column(String(50), nullable=True)
	tcpsequence   = Column(String(200), nullable=True)
	hostname      = Column(Text, nullable=True)
	vendor        = Column(Text, nullable=True)
	uptime        = Column(String(100), nullable=True)
	lastboot      = Column(String(100), nullable=True)
	distance      = Column(Integer, nullable=True)
	latitude      = Column(Float, nullable=True)
	longitude     = Column(Float, nullable=True)
	scripts       = Column(Text, nullable=True)
	scope         = Column(Boolean, default=False)
	country_code  = Column(String(3), nullable=True)
	country_name  = Column(String(100), nullable=True)
	isp           = Column(String(100), nullable=True)
	organization  = Column(String(100), nullable=True)
