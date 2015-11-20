#!/usr/bin/env python
"""\
Check for inconsistencies and missing info in conference program data.

Exit code == 0 and no output means success.

Exit code == 0 and output on stdout means validation error found.

Exit code != 0 means other error, details/traceback on stderr.
"""
import codecs
import optparse
import os
import sys

import yaml

# Ugly hack: only ever write utf-8 to stdout, especially if it is a pipe with no encoding set.
# Better solution: port to python3.
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

class Options(optparse.OptionParser):
    
    def __init__(self):
        global __doc__
        optparse.OptionParser.__init__(
            self, usage="%prog [options]",
            description=__doc__)
        self.add_option(
            '-d', '--sitedir', action='store', default=os.path.dirname(os.path.dirname(__file__)),
            help=("Site root directory."))

def usage(message):
    sys.stderr.write(message + "\n")
    sys.stderr.write(Options().get_usage())
    return os.EX_USAGE

class ValidationError(Exception):
    """Raised on finding inconsistent data."""

def error(msg, *args, **kw):
    if args:
        msg %= args
    elif kw:
        msg %= kw
    raise ValidationError(msg)

def _get(datadict, key, default=[]):
    return datadict.get(key, None) or default

datasets = [
    'people',
    'program',
    'sessions',
    ]

def load_dataset(datadir, dataset):
    return yaml.load(open(os.path.join(datadir, dataset + '.yml')))

def load_data(datadir):
    event = dict()
    for dataset in datasets:
        event[dataset] = load_dataset(datadir, dataset)
    return event

### General purpose 

def assert_string_keys(label, datadict):
    for k in datadict.keys():
        if not isinstance(k, str):
            error("%s %r incorrect key type, must be a string.", label, k)

def assert_value_data_types(label, datadict, datatype, *keys):
    if not keys:
        keys = datadict.keys()
    for k in keys:
        value = datadict.get(k, None)
        if value and not isinstance(value, datatype):
            error("%s %s %r must be %s.", label, k, value, datatype)

def assert_item_data_types(label, datalist, datatype):
    for i, item in enumerate(datalist):
        if not isinstance(item, datatype):
            error("%s %s must be %s.", label, i + 1, datatype)

### People

def validate_people(persons):
    assert_string_keys('Person', persons)
    for id, person in persons.items():
        assert_value_data_types('Person %r' % id, person, basestring, 'area', 'name', 'home', 'role', 'size')
        assert_value_data_types('Person %r' % id, person, str, 'email')
        assert_value_data_types('Person %r' % id, person, (basestring, int), 'arrival', 'departure')
        assert_value_data_types('Person %r' % id, person, bool, 'shuttle')
        if not person.get('name', None):
            error("Person %r has no name.", id)

### Sessions

def validate_slides(label, slides):
    assert_item_data_types(label, slides, str)

def validate_panel(label, slides):
    assert_item_data_types(label, slides, str)

def validate_talk(label, talk):
    assert_string_keys(label, talk)
    assert_value_data_types(label, talk, str, 'speaker')
    assert_value_data_types(label, talk, basestring, 'title')
    assert_value_data_types(label, talk, bool, 'abstract')
    assert_value_data_types(label, talk, (list, str), 'slides', 'panel')
    slides = talk.get('slides', None)
    if isinstance(slides, list):
        validate_slides(label + ' slides', slides)
    panel = talk.get('panel', None)
    if isinstance(panel, list):
        validate_panel(label + ' panel', _get(talk, 'panel'))

def validate_talks(label, talks):
    assert_item_data_types(label, talks, dict)
    for i, talk in enumerate(talks):
        talk_label = label + ' %s' % (i + 1)
        validate_talk(talk_label, talk)

def validate_sessions(sessions):
    assert_string_keys('Session', sessions)
    for id, session in sessions.items():
        label = 'Session %r' % id
        assert_string_keys(label, session)
        assert_value_data_types(label, session, str, 'chair')
        assert_value_data_types(label, session, basestring, 'title', 'room')
        assert_value_data_types(label, session, bool, 'abstract', 'plenary')
        assert_value_data_types(label, session, list, 'talks')
        validate_talks(label + ' talk', _get(session, 'talks'))

### Program

def validate_slots(label, slots):
    assert_string_keys(label, slots)
    assert_value_data_types(label, slots, basestring)

def validate_day(label, day):
    assert_string_keys(label, day)
    assert_value_data_types(label, day, basestring, 'title')
    assert_value_data_types(label, day, dict, 'slots')
    validate_slots(label + ' schedule', _get(day, 'slots', {}))

def validate_program(program):
    assert_item_data_types('Program day', program, dict)
    for i, day in enumerate(program):
        validate_day('Program day %s' % (i + 1), day)

### Consistency checks

def assert_consistency_sessions_persons(sessions, persons):
    for session_id, session in sessions.items():
        chair = session.get('chair', None)
        if chair and chair not in persons:
            error("Session %r chair %r does not exist in persons.yml.", session_id, chair)
        for i, talk in enumerate(_get(session, 'talks')):
            speaker = talk.get('speaker', None)
            if speaker and speaker not in persons:
                error("Session %r talk %s: Speaker %r does not exist in persons register.", 
                    session['id'], i + 1, speaker)
            for j, panel_member in enumerate(_get(talk, 'panel')):
                if panel_member not in persons:
                    error("Session %r talk %s panel member %s %r does not exist in persons register.", 
                        session['id'], i + 1, j + 1, panel_member)

def assert_consistent_day_program_sessions(label, day, sessions):
    for slot, activity in _get(sessions, 'schedule', {}).items():
        if activity.lower().startswith('session'):
            starting = activity.split()[1:]
            for id in starting:
                if id not in sessions:
                    error("%s slot %r session %r does not exist in sessions.yml.", label, slot, id)

def assert_consistent_program_sessions(program, sessions):
    for i, day in enumerate(program):
        assert_consistent_day_program_sessions("Program day %s" % (i+ 1), day, sessions)

### Full integrity check 

def integrity_check(event):
    validate_people(event['people'])
    validate_sessions(event['sessions'])
    validate_program(event['program'])
    assert_consistency_sessions_persons(event['sessions'], event['people'])
    assert_consistent_program_sessions(event['program'], event['sessions'])
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
    options, args = Options().parse_args(argv[1:])
    if args:
        return usage("This program takes no arguments.")
    event = load_data(os.path.join(options.sitedir, '_data'))
    try:
        integrity_check(event)
    except ValidationError as e:
        print ', '.join(str(arg) for arg in e.args)
    return 0
    
if __name__ == '__main__':
    sys.exit(main())

