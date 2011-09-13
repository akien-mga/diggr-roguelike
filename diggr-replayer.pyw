
import cPickle
import time
import string
import os

import libtcodpy as libtcod

import sqlite3

import diggr

Item = diggr.Item

def main():

    w = 80
    h = 25

    diggr._inputs = []

    font = 'terminal10x16_gs_ro.png'
    libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(w, h, 'Diggr game replayer tool', False, libtcod.RENDERER_SDL)
    libtcod.sys_set_fps(30)

    libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.white, libtcod.black)
    libtcod.console_set_color_control(libtcod.COLCTRL_2, libtcod.darker_green, libtcod.black)
    libtcod.console_set_color_control(libtcod.COLCTRL_3, libtcod.yellow, libtcod.black)
    libtcod.console_set_color_control(libtcod.COLCTRL_4, libtcod.red, libtcod.black)
    libtcod.console_set_color_control(libtcod.COLCTRL_5, libtcod.gray, libtcod.black)

    _c1 = libtcod.COLCTRL_1
    _c2 = libtcod.COLCTRL_2
    _c3 = libtcod.COLCTRL_3
    _c4 = libtcod.COLCTRL_4
    _c5 = libtcod.COLCTRL_5


    def input_name():
        name = ''
        while 1:
            k3 = diggr.draw_window(['Enter filename: ' + name], w, h)
            if k3 in '\n\r':
                break
            elif k3 in string.ascii_letters or k3 in string.digits or k3 in '.':
                name += k3
            elif ord(k3) == 8 or ord(k3) == 127:
                if len(name) > 0:
                    name = name[:-1]

        return name


    n = 0
    limit = 9

    conn = sqlite3.connect('highscore.db')
    c = conn.cursor()

    mode = 1
    achievement = None

    tbl_games = 'Games%s' % diggr._version.replace('.', '')
    tbl_achievements = 'Achievements%s' % diggr._version.replace('.', '')



    while 1:
        if libtcod.console_is_window_closed():
            break

        if mode == 1:
            if achievement:
                c.execute('select id, seed, score from %s join %s on (game_id = id) '
                          ' where achievement = ? order by seed desc'
                          ' limit %d offset %d' % (tbl_games, tbl_achievements, limit, n),
                          (achievement,))
            else:
                c.execute('select id, seed, score from %s order by seed desc '
                          'limit %d offset %d' % (tbl_games, limit, n))

        elif mode == 2:
            if achievement:
                c.execute('select id, seed, score from %s join %s on (game_id = id) '
                          ' where achievement = ? order by score desc'
                          ' limit %d offset %d' % (tbl_games, tbl_achievements, limit, n),
                          (achievement,))
            else:
                c.execute('select id, seed, score from %s order by score desc '
                          'limit %d offset %d' % (tbl_games, limit, n))


        qq = 0
        choice = {}
        s = []

        for gameid,seed,score in c.fetchall():
            chh = chr(97+qq)
            s.append('')
            s.append('%c%c)%c  Game #%c%d%c at %s, score %c%d%c' % \
                     (_c1, chh, _c2, _c1, gameid, _c5,
                      time.ctime(seed), _c1, score, _c5))
            qq += 1
            choice[chh] = gameid

        s.append('')
        s.append(":  Left and right keys to scroll entries")
        s.append(":  Type its letter to select an entry")
        s.append(":  '?' for help; Other keys: s, w, z, q")
        s.append('')
        s.append('*WARNING*: Only games from the _same_ version of Diggr will replay correctly!')

        k = diggr.draw_window(s, w, h, True)

        if k == 'h':
            n -= limit
            if n < 0:
                n = 0

        elif k == 'l':
            if len(choice) > 0:
                n += limit

        elif k == '?':
            s = ['',
                 'Left and right keys to scroll entries.',
                 'Type its letter to select an entry.',
                 ''
                 ' s : Switch sorting mode between "date" and "score".',
                 ' w : Filter scores by achievement.',
                 ' z : Load scores from another file on disk.',
                 ' q : Quit.'
                 '']
            diggr.draw_window(s, w, h)


        elif k == 's':
            if mode == 1:
                mode = 2
            else:
                mode = 1
            n = 0

        elif k == 'w':

            n2 = 0
            limit2 = 9

            while 1:
                c.execute('select achievement, count(*) from %s join %s '
                          'on (game_id = id) group by 1 order by 2 desc '
                          ' limit %d offset %d' % (tbl_games, tbl_achievements, limit2, n2))

                s = []
                qq = 0
                choices2 = {}
                for aach,cnt in c.fetchall():
                    aach = aach.encode('ascii')
                    chh = chr(97+qq)
                    s.append('')
                    s.append('%c%c%c) %c%s%c: %s%d games' % \
                             (_c1, chh, _c5, _c1, aach, _c5, ' '*(max(0, 50-len(aach))), cnt))
                    qq += 1
                    choices2[chh] = aach

                k2 = diggr.draw_window(s, w, h, True)

                if k2 == 'h':
                    n2 -= limit
                    if n2 < 0:
                        n2 = 0

                elif k2 == 'l':
                    if len(choices2) > 0:
                        n2 += limit

                elif k2 in choices2:
                    achievement = choices2[k2]
                    n = 0
                    break

                else:
                    achievement = None
                    n = 0
                    break

        elif k in choice:
            gameid = choice[k]

            s2 = ['',
                  'Do what?',
                  '  a) replay this game',
                  '  b) save this game to a file on disk',
                  '',
                  'Achievements of this game:',
                  '']

            c.execute('select achievement from %s where game_id = %d' % (tbl_achievements, gameid))

            for aach in c.fetchall():
                aach = aach[0].encode('ascii')
                s2.append('    ' + aach)

            k2 = diggr.draw_window(s2, w, h, True)

            if k2 == 'a':
                c.execute('select seed, inputs, bones from %s where id = %d' % \
                          (tbl_games, gameid))

                seed,inputs,bones = c.fetchone()
                inputs = cPickle.loads(str(inputs))
                bones = cPickle.loads(str(bones))

                ok = diggr.main(replay=(seed,inputs,bones))
                if not ok:
                    diggr.draw_window(['Wrong version of replay file!'],
                                      w, h)

                if len(diggr._inputqueue) != 0:
                    raise Exception('Malformed replay file.')
                diggr._inputqueue = None

            elif k2 == 'b':
                name = input_name()

                if len(name) > 0:

                    name = os.path.join('replays', name)
                    conn2 = sqlite3.connect(name)
                    c2 = conn2.cursor()

                    c2.execute('create table if not exists ' + tbl_games + \
                               ' (id INTEGER PRIMARY KEY, seed int, score int, bones blob, inputs blob)')
                    c2.execute('create table if not exists ' + tbl_achievements + \
                               ' (achievement text, game_id int)')

                    c.execute('select seed, score, bones, inputs from %s where id = %d' % \
                              (tbl_games, gameid))

                    for seed,score,bones,inputs in c.fetchall():
                        c2.execute('insert into ' + tbl_games + '(id, seed, score, bones, inputs) values (NULL, ?, ?, ?, ?)',
                                   (seed, score, bones, inputs))
                        gameid2 = c2.lastrowid
                        c.execute('select achievement from %s where game_id = %d' % (tbl_achievements, gameid))
                        for ach in c.fetchall():
                            ach = ach[0]
                            c2.execute('insert into ' + tbl_achievements + '(achievement, game_id) values (?, ?)',
                                       (ach, gameid2))

                    conn2.commit()
                    c2.close()
                    conn2.close()
                    diggr.draw_window(['Saved to "%s".' % name,
                                       'Press any key to continue.'], w, h)



        elif k == 'z':
            name = input_name()

            if len(name) > 0:
                name = os.path.join('replays', name)

                ok = True
                try:
                    os.stat(name)
                except:
                    diggr.draw_window(['File not found: "%s".' % name,
                                       'Press any key to continue.'], w, h)
                    ok = False

                if ok:
                    c.close()
                    conn.close()
                    conn = sqlite3.connect(name)
                    c = conn.cursor()
                    n = 0
            else:
                c.close()
                conn.close()
                conn = sqlite3.connect('highscore.db')
                c = conn.cursor()
                n = 0


        elif k == 'q':
            break



if __name__ == '__main__':
    main()
