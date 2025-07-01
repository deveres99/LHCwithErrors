import xtrack as xt

def slice_env(env, slicefactor=4):
    for line in env.lines.values():
        line.slice_thick_elements(slicing_strategies=[
            xt.Strategy(slicing=xt.Teapot(2)),  # Default slicing for all elements
            xt.Strategy(slicing=xt.Teapot(2 * slicefactor), name="mq\..*"),
            xt.Strategy(slicing=xt.Teapot(32 * slicefactor), name="mqxa\..*"),
            xt.Strategy(slicing=xt.Teapot(32 * slicefactor), name="mqxb\..*"),
            xt.Strategy(slicing=xt.Teapot(4), name="mbx\..*"),
            xt.Strategy(slicing=xt.Teapot(4), name="mbrb\..*"),
            xt.Strategy(slicing=xt.Teapot(4), name="mbrc\..*"),
            xt.Strategy(slicing=xt.Teapot(4), name="mbrs\..*"),
            xt.Strategy(slicing=xt.Teapot(4), name="mqwa\..*"),
            xt.Strategy(slicing=xt.Teapot(4), name="mqwb\..*"),
            xt.Strategy(slicing=xt.Teapot(4 * slicefactor), name="mqy\..*"),
            xt.Strategy(slicing=xt.Teapot(4 * slicefactor), name="mqm\..*"),
            xt.Strategy(slicing=xt.Teapot(4 * slicefactor), name="mqmc\..*"),
            xt.Strategy(slicing=xt.Teapot(4 * slicefactor), name="mqml\..*"),
            xt.Strategy(slicing=xt.Teapot(2 * slicefactor), name="mqtlh\..*"),
            xt.Strategy(slicing=xt.Teapot(2 * slicefactor), name="mqtli\..*"),
            xt.Strategy(slicing=xt.Teapot(2 * slicefactor), name="mqt\..*"),
            xt.Strategy(slicing=None, element_type=xt.Solenoid)
        ])
