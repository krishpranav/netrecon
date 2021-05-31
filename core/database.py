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

class services(Base):
	__tablename__ = "services"

	id          = Column(Integer, primary_key=True)
	port        = Column(Integer, nullable=False)
	protocol    = Column(String(3), nullable=False)
	service     = Column(String(200), nullable=False)
	fingerprint = Column(Text, nullable=True)
	state       = Column(String(200), nullable=False)
	banner      = Column(Text, nullable=True)
	host        = relationship(targets)
	host_id     = Column(Integer, ForeignKey('targets.id'))

class activity_log(Base):
	__tablename__ = "activity_log"

	id         = Column(Integer, primary_key=True)
	pid        = Column(Integer, nullable=False)
	start_time = Column(String(200), nullable=False)
	end_time   = Column(String(200), nullable=False)
	title      = Column(String(200), nullable=False)
	output     = Column(Text, nullable=True)
	extension  = Column(Text, nullable=True)
	target     = Column(Text, nullable=True)

class notes(Base):
	__tablename__ = "notes"

	id      = Column(Integer, primary_key=True)
	host    = relationship(targets)
	host_id = Column(Integer, ForeignKey("targets.id"))
	title   = Column(String(200))
	text    = Column(Text)


class DB:
    
    
    def __init__(self, db_loc):
        
        engine = create_engine("sqlite:///"+db_loc)
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)

        self.db_loc = db_loc
        self.session = DBSession()

        self.nmap_service_loc = "/usr/share/nmap/nmap-services"

    
    def _find_nmap_service(self, port, transport):
        with open(self.nmap_service_loc, 'r') as f:
            for line in f.readlines():
                if str(port)+"/"+transport in line:
                    return line.split()[0]

    def switch_scope(self, value, host):
        host.scope = value
        self.session.add(host)
        self.session.commit()
        