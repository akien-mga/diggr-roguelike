#ifndef __MONSTERS_H
#define __MONSTERS_H

#include <unordered_map>


namespace monsters {

typedef std::pair<unsigned int, unsigned int> pt;


struct Monster {
    std::string tag;
    pt xy;

    Monster() : xy(0, 0) {}

    Monster(const std::string& _tag, const pt& _xy) : 
        tag(_tag), xy(_xy) 
        {}
};


}


namespace serialize {

template <>
struct reader<monsters::Monster> {
    void read(Source& s, monsters::Monster& m) {
        serialize::read(s, m.tag);
        serialize::read(s, m.xy);
    }
};

template <>
struct writer<monsters::Monster> {
    void write(Sink& s, const monsters::Monster& m) {
        serialize::write(s, m.tag);
        serialize::write(s, m.xy);
    }
};

}


namespace monsters {

struct Monsters {

    std::unordered_map<pt, Monster> mons;

    void init() {
        mons.clear();
    }

    void clear() {
        init();
    }

    
    template <typename FUNC, typename FUNCP>
    void place_clump(neighbors::Neighbors& neigh, rnd::Generator& rng, grid::Map& grid,
                     const std::string& tag, unsigned int n,
                     FUNC f, FUNCP fp) {

        std::unordered_set<pt> clump;

        for (unsigned int j = 0; j < n; ++j) {
                    
            if (clump.empty()) {
                pt tmp;
                if (!f(grid, rng, tmp)) 
                    break;

                clump.insert(tmp);
            }

            pt xy = *(clump.begin());
            clump.erase(clump.begin());

            mons[xy] = Monster(tag, xy);
            grid.add_nogen(xy.first, xy.second);

            std::cout << "  .. clump: " << j << " ~ " << xy.first << "," << xy.second << std::endl;

            for (const pt& v : neigh(xy)) {

                if (fp(grid, v.first, v.second) && !grid.is_nogen(v.first, v.second)) {
                    clump.insert(v);
                }
            }
        }
    }

    template <typename FUNC>
    void place_scatter(rnd::Generator& rng, grid::Map& grid, const std::string& tag, unsigned int n, FUNC f) {

        for (unsigned int j = 0; j < n; ++j) {

            pt xy;

            if (!f(grid, rng, xy))
                break;

            mons[xy] = Monster(tag, xy);
            grid.add_nogen(xy.first, xy.second);
        }
    }

        
    void generate(neighbors::Neighbors& neigh, rnd::Generator& rng, grid::Map& grid, counters::Counts& counts, 
                  unsigned int level, unsigned int n) {

        std::cout << "!!! " << level << " " << n << std::endl;

        std::map<std::string, unsigned int> q = counts.take(rng, level, n);

        bm _z("monster placement");

        for (const auto& i : q) {

            Species::habitat_t h = species().get(i.first).habitat; 
    
            std::cout << "!-| " << i.first << " " << i.second << " " << (int)h << std::endl;


            switch (h) {

            case Species::habitat_t::walk:
                place_scatter(rng, grid, i.first, i.second, std::mem_fn(&grid::Map::one_of_walk));
                break;

            case Species::habitat_t::floor:
                place_scatter(rng, grid, i.first, i.second, std::mem_fn(&grid::Map::one_of_floor));
                break;

            case Species::habitat_t::water:
                place_scatter(rng, grid, i.first, i.second, std::mem_fn(&grid::Map::one_of_water));
                break;

            case Species::habitat_t::corner:
                place_scatter(rng, grid, i.first, i.second, std::mem_fn(&grid::Map::one_of_corner));
                break;

            case Species::habitat_t::shoreline:
                place_scatter(rng, grid, i.first, i.second, std::mem_fn(&grid::Map::one_of_shore));
                break;

            case Species::habitat_t::clumped_floor:
                place_clump(neigh, rng, grid, i.first, i.second, 
                            std::mem_fn(&grid::Map::one_of_floor), std::mem_fn(&grid::Map::is_floor));
                break;

            case Species::habitat_t::clumped_water:
                place_clump(neigh, rng, grid, i.first, i.second, 
                            std::mem_fn(&grid::Map::one_of_water), std::mem_fn(&grid::Map::is_water));
                break;

            }
        }
    }

    bool get(unsigned int x, unsigned int y, Monster& ret) {
        auto i = mons.find(pt(x, y));

        if (i == mons.end()) {
            return false;
        }

        ret = i->second;
        return true;
    }

    void dispose(counters::Counts& counts) {

        for (const auto& i : mons) {
            const Species& s = species().get(i.second.tag);
            counts.replace(s.level, s.tag);
        }
    }

    template <typename FUNC>
    void process(grender::Grid& grid, FUNC f) {

        size_t sbefore = mons.size();

        std::unordered_map<pt, Monster> neuw;
        std::unordered_set<pt> wipe;

        for (const auto& i : mons) {
            const Species& s = species().get(i.second.tag);

            pt nxy;

            if (f(i.second, s, nxy) && neuw.count(nxy) == 0) {

                neuw[nxy] = i.second;
            }
        }

        for (auto& i : neuw) {
            if (mons.count(i.first) == 0 || wipe.count(i.first) != 0) {

                wipe.insert(i.second.xy);

                i.second.xy = i.first;
                mons[i.first] = i.second;

                wipe.erase(i.first);

                grid.invalidate(i.first.first, i.first.second);

            }
        }

        for (const pt& i : wipe) {
            mons.erase(i);

            grid.invalidate(i.first, i.second);
        }

        if (mons.size() != sbefore) {

            for (const auto& i : mons) {
                std::cout << "   | " << i.first.first << "," << i.first.second << std::endl;
            }
            std::cout << mons.size() << " " << sbefore << std::endl;

            throw std::runtime_error("Lost a monster in monster::process()!");
        }
    }

    inline void write(serialize::Sink& s) {
        serialize::write(s, mons);
    }

    inline void read(serialize::Source& s) {
        serialize::read(s, mons);
    }
};


}

#endif