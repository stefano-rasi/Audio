import numpy as np

class Envelope:
    def __init__(self, attack_samples, release_samples):
        self.a = 0
        self.r = 0

        self.released = False

        self.attack_samples = attack_samples
        self.release_samples = release_samples

        self.last_attack_sample = 1

    def take(self, sample_count):
        if not self.released and self.a < len(self.attack_samples):
            start = self.a

            stop = self.a + sample_count

            self.a += sample_count

            samples = self.attack_samples.take(range(start, stop), mode='clip')

            self.last_attack_sample = samples[-1]

            return samples
        elif not self.released:
            sample = self.last_attack_sample

            samples = np.repeat(sample, sample_count)

            return samples
        elif self.release_samples.size:
            if self.r >= len(self.release_samples):
                return None
            elif self.r + sample_count < len(self.release_samples):
                start = self.r

                stop = self.r + sample_count

                self.r += sample_count

                samples = self.release_samples[start:stop]

                return self.last_attack_sample * samples
            else:
                samples = np.zeros(sample_count)

                start = self.r

                stop = min(self.r + sample_count, len(self.release_samples))

                samples[:stop-start] = self.release_samples[start:stop]

                self.r += sample_count

                return self.last_attack_sample * samples
        else:
            return None

    def release(self):
        self.released = True