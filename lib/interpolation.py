class Interpolation:
    def __init__(self, values):
        self.values = values

    def interpolate(self, value):
        stop = None
        start = None

        for stop, _ in self.values:
            if stop > value:
                break

            start = i

        if value == start:
            return values[start]
        else
            amount = (stop - start) / (value - start)

            return values[start] * amount + values[stop] * (1 - amount)