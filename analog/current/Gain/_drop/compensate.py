from .. import Base

class Modificator(Base):
    """**Compensating Base-Emiiter Forward Voltage Drop**

    Wouldn’t it be nice if an emitter follower did not cause an offset of the output signal by the `V_(BE) ≈ 0.6 V` base–emitter drop? Block shows how to cancel the dc offset, by cascading a pnp follower (which has a positive `V_(BE)` offset) with an npn follower (which has a comparable negative `V_(BE)` offset).

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 85
    """

    pass