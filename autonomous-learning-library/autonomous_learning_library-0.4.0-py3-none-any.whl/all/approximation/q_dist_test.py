import unittest
import torch
from torch import nn
import torch_testing as tt
from all.environments import State
from all.approximation import QDist

STATE_DIM = 1
ACTIONS = 2
ATOMS = 5
V_MIN = -2
V_MAX = 2


class TestQDist(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(2)
        self.model = nn.Sequential(nn.Linear(STATE_DIM, ACTIONS * ATOMS))
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=0.1)
        self.q = QDist(self.model, self.optimizer, ACTIONS, ATOMS, V_MIN, V_MAX)

    def test_atoms(self):
        tt.assert_almost_equal(self.q.atoms, torch.tensor([-2, -1, 0, 1, 2]))

    def test_q_values(self):
        states = State(torch.randn((3, STATE_DIM)))
        probs = self.q(states)
        self.assertEqual(probs.shape, (3, ACTIONS, ATOMS))
        tt.assert_almost_equal(
            probs.sum(dim=2),
            torch.tensor([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]),
            decimal=3,
        )
        tt.assert_almost_equal(
            probs,
            torch.tensor(
                [
                    [
                        [0.2065, 0.1045, 0.1542, 0.2834, 0.2513],
                        [0.3903, 0.2471, 0.0360, 0.1733, 0.1533],
                    ],
                    [
                        [0.1966, 0.1299, 0.1431, 0.3167, 0.2137],
                        [0.3190, 0.2471, 0.0534, 0.1424, 0.2380],
                    ],
                    [
                        [0.1427, 0.2486, 0.0946, 0.4112, 0.1029],
                        [0.0819, 0.1320, 0.1203, 0.0373, 0.6285],
                    ],
                ]
            ),
            decimal=3,
        )

    def test_single_q_values(self):
        states = State(torch.randn((3, STATE_DIM)))
        actions = torch.tensor([0, 1, 0])
        probs = self.q(states, actions)
        self.assertEqual(probs.shape, (3, ATOMS))
        tt.assert_almost_equal(
            probs.sum(dim=1), torch.tensor([1.0, 1.0, 1.0]), decimal=3
        )
        tt.assert_almost_equal(
            probs,
            torch.tensor(
                [
                    [0.2065, 0.1045, 0.1542, 0.2834, 0.2513],
                    [0.3190, 0.2471, 0.0534, 0.1424, 0.2380],
                    [0.1427, 0.2486, 0.0946, 0.4112, 0.1029],
                ]
            ),
            decimal=3,
        )

    def test_done(self):
        states = State(torch.randn((3, STATE_DIM)), mask=torch.tensor([1, 0, 1]))
        probs = self.q(states)
        self.assertEqual(probs.shape, (3, ACTIONS, ATOMS))
        tt.assert_almost_equal(
            probs.sum(dim=2),
            torch.tensor([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]),
            decimal=3,
        )
        tt.assert_almost_equal(
            probs,
            torch.tensor(
                [
                    [
                        [0.2065, 0.1045, 0.1542, 0.2834, 0.2513],
                        [0.3903, 0.2471, 0.0360, 0.1733, 0.1533],
                    ],
                    [[0, 0, 1, 0, 0], [0, 0, 1, 0, 0]],
                    [
                        [0.1427, 0.2486, 0.0946, 0.4112, 0.1029],
                        [0.0819, 0.1320, 0.1203, 0.0373, 0.6285],
                    ],
                ]
            ),
            decimal=3,
        )

    def test_reinforce(self):
        states = State(torch.randn((3, STATE_DIM)))
        actions = torch.tensor([0, 1, 0])
        original_probs = self.q(states, actions)
        tt.assert_almost_equal(
            original_probs,
            torch.tensor(
                [
                    [0.2065, 0.1045, 0.1542, 0.2834, 0.2513],
                    [0.3190, 0.2471, 0.0534, 0.1424, 0.2380],
                    [0.1427, 0.2486, 0.0946, 0.4112, 0.1029],
                ]
            ),
            decimal=3,
        )

        target_dists = torch.tensor(
            [[0, 0, 1, 0, 0], [0, 0, 0, 0, 1], [0, 1, 0, 0, 0]]
        ).float()

        def _loss(dist, target_dist):
            log_dist = torch.log(torch.clamp(dist, min=1e-5))
            log_target_dist = torch.log(torch.clamp(target_dist, min=1e-5))
            return (target_dist * (log_target_dist - log_dist)).sum(dim=-1).mean()

        self.q.reinforce(_loss(original_probs, target_dists))

        new_probs = self.q(states, actions)
        tt.assert_almost_equal(
            torch.sign(new_probs - original_probs), torch.sign(target_dists - 0.5)
        )

    # pylint: disable=bad-whitespace,bad-continuation
    def test_project_dist(self):
        # This gave problems in the past between different cuda version,
        # so a test was added.
        q = QDist(self.model, self.optimizer, ACTIONS, 51, -10., 10.)
        dist = torch.tensor([
            [0.0190, 0.0197, 0.0200, 0.0190, 0.0195, 0.0198, 0.0194, 0.0192, 0.0201,
            0.0203, 0.0189, 0.0190, 0.0199, 0.0193, 0.0192, 0.0199, 0.0198, 0.0197,
            0.0193, 0.0198, 0.0192, 0.0191, 0.0200, 0.0202, 0.0191, 0.0202, 0.0198,
            0.0200, 0.0198, 0.0193, 0.0192, 0.0202, 0.0192, 0.0194, 0.0199, 0.0197,
            0.0197, 0.0201, 0.0199, 0.0190, 0.0192, 0.0195, 0.0202, 0.0194, 0.0203,
            0.0201, 0.0190, 0.0192, 0.0201, 0.0201, 0.0192],
            [0.0191, 0.0197, 0.0200, 0.0190, 0.0195, 0.0198, 0.0194, 0.0192, 0.0201,
            0.0203, 0.0190, 0.0190, 0.0199, 0.0193, 0.0192, 0.0199, 0.0198, 0.0197,
            0.0193, 0.0198, 0.0192, 0.0191, 0.0200, 0.0202, 0.0191, 0.0202, 0.0198,
            0.0200, 0.0198, 0.0193, 0.0192, 0.0202, 0.0192, 0.0194, 0.0199, 0.0197,
            0.0197, 0.0200, 0.0199, 0.0190, 0.0192, 0.0195, 0.0202, 0.0194, 0.0203,
            0.0201, 0.0190, 0.0192, 0.0201, 0.0200, 0.0192],
            [0.0191, 0.0197, 0.0200, 0.0190, 0.0195, 0.0198, 0.0194, 0.0192, 0.0200,
            0.0203, 0.0190, 0.0191, 0.0199, 0.0193, 0.0192, 0.0199, 0.0198, 0.0197,
            0.0193, 0.0198, 0.0192, 0.0191, 0.0199, 0.0202, 0.0192, 0.0202, 0.0198,
            0.0200, 0.0198, 0.0193, 0.0192, 0.0202, 0.0192, 0.0194, 0.0199, 0.0197,
            0.0197, 0.0200, 0.0199, 0.0190, 0.0192, 0.0195, 0.0202, 0.0194, 0.0203,
            0.0201, 0.0190, 0.0192, 0.0201, 0.0200, 0.0192]
        ])
        support = torch.tensor([
            [-9.7030, -9.3149, -8.9268, -8.5386, -8.1505, -7.7624, -7.3743, -6.9862,
            -6.5980, -6.2099, -5.8218, -5.4337, -5.0456, -4.6574, -4.2693, -3.8812,
            -3.4931, -3.1050, -2.7168, -2.3287, -1.9406, -1.5525, -1.1644, -0.7762,
            -0.3881,  0.0000,  0.3881,  0.7762,  1.1644,  1.5525,  1.9406,  2.3287,
            2.7168,  3.1050,  3.4931,  3.8812,  4.2693,  4.6574,  5.0456,  5.4337,
            5.8218,  6.2099,  6.5980,  6.9862,  7.3743,  7.7624,  8.1505,  8.5386,
            8.9268,  9.3149,  9.7030],
            [-9.7030, -9.3149, -8.9268, -8.5386, -8.1505, -7.7624, -7.3743, -6.9862,
            -6.5980, -6.2099, -5.8218, -5.4337, -5.0456, -4.6574, -4.2693, -3.8812,
            -3.4931, -3.1050, -2.7168, -2.3287, -1.9406, -1.5525, -1.1644, -0.7762,
            -0.3881,  0.0000,  0.3881,  0.7762,  1.1644,  1.5525,  1.9406,  2.3287,
            2.7168,  3.1050,  3.4931,  3.8812,  4.2693,  4.6574,  5.0456,  5.4337,
            5.8218,  6.2099,  6.5980,  6.9862,  7.3743,  7.7624,  8.1505,  8.5386,
            8.9268,  9.3149,  9.7030],
            [-9.7030, -9.3149, -8.9268, -8.5386, -8.1505, -7.7624, -7.3743, -6.9862,
            -6.5980, -6.2099, -5.8218, -5.4337, -5.0456, -4.6574, -4.2693, -3.8812,
            -3.4931, -3.1050, -2.7168, -2.3287, -1.9406, -1.5525, -1.1644, -0.7762,
            -0.3881,  0.0000,  0.3881,  0.7762,  1.1644,  1.5525,  1.9406,  2.3287,
            2.7168,  3.1050,  3.4931,  3.8812,  4.2693,  4.6574,  5.0456,  5.4337,
            5.8218,  6.2099,  6.5980,  6.9862,  7.3743,  7.7624,  8.1505,  8.5386,
            8.9268,  9.3149,  9.7030]
        ])
        expected = torch.tensor([
            [0.0049, 0.0198, 0.0204, 0.0202, 0.0198, 0.0202, 0.0202, 0.0199, 0.0202,
            0.0208, 0.0201, 0.0195, 0.0201, 0.0201, 0.0198, 0.0203, 0.0204, 0.0203,
            0.0200, 0.0203, 0.0199, 0.0197, 0.0205, 0.0208, 0.0197, 0.0214, 0.0204,
            0.0206, 0.0203, 0.0199, 0.0199, 0.0206, 0.0198, 0.0201, 0.0204, 0.0203,
            0.0204, 0.0206, 0.0201, 0.0197, 0.0199, 0.0204, 0.0204, 0.0205, 0.0208,
            0.0200, 0.0197, 0.0204, 0.0207, 0.0200, 0.0049],
            [0.0049, 0.0198, 0.0204, 0.0202, 0.0198, 0.0202, 0.0202, 0.0199, 0.0202,
            0.0208, 0.0202, 0.0196, 0.0201, 0.0201, 0.0198, 0.0203, 0.0204, 0.0203,
            0.0200, 0.0203, 0.0199, 0.0197, 0.0205, 0.0208, 0.0197, 0.0214, 0.0204,
            0.0206, 0.0203, 0.0199, 0.0199, 0.0206, 0.0198, 0.0201, 0.0204, 0.0203,
            0.0204, 0.0206, 0.0201, 0.0197, 0.0199, 0.0204, 0.0204, 0.0205, 0.0208,
            0.0200, 0.0197, 0.0204, 0.0206, 0.0200, 0.0049],
            [0.0049, 0.0198, 0.0204, 0.0202, 0.0198, 0.0202, 0.0202, 0.0199, 0.0202,
            0.0208, 0.0202, 0.0196, 0.0202, 0.0201, 0.0198, 0.0203, 0.0204, 0.0203,
            0.0200, 0.0203, 0.0199, 0.0197, 0.0204, 0.0208, 0.0198, 0.0214, 0.0204,
            0.0206, 0.0203, 0.0199, 0.0199, 0.0206, 0.0198, 0.0201, 0.0204, 0.0203,
            0.0204, 0.0206, 0.0201, 0.0197, 0.0199, 0.0204, 0.0204, 0.0205, 0.0208,
            0.0200, 0.0197, 0.0204, 0.0206, 0.0200, 0.0049]
        ])
        tt.assert_almost_equal(q.project(dist, support).cpu(), expected.cpu(), decimal=3)

    def test_project_dist_cuda(self):
        if torch.cuda.is_available():
            # This gave problems in the past between different cuda version,
            # so a test was added.
            q = QDist(self.model.cuda(), self.optimizer, ACTIONS, 51, -10., 10.)
            dist = torch.tensor([
                [0.0190, 0.0197, 0.0200, 0.0190, 0.0195, 0.0198, 0.0194, 0.0192, 0.0201,
                0.0203, 0.0189, 0.0190, 0.0199, 0.0193, 0.0192, 0.0199, 0.0198, 0.0197,
                0.0193, 0.0198, 0.0192, 0.0191, 0.0200, 0.0202, 0.0191, 0.0202, 0.0198,
                0.0200, 0.0198, 0.0193, 0.0192, 0.0202, 0.0192, 0.0194, 0.0199, 0.0197,
                0.0197, 0.0201, 0.0199, 0.0190, 0.0192, 0.0195, 0.0202, 0.0194, 0.0203,
                0.0201, 0.0190, 0.0192, 0.0201, 0.0201, 0.0192],
                [0.0191, 0.0197, 0.0200, 0.0190, 0.0195, 0.0198, 0.0194, 0.0192, 0.0201,
                0.0203, 0.0190, 0.0190, 0.0199, 0.0193, 0.0192, 0.0199, 0.0198, 0.0197,
                0.0193, 0.0198, 0.0192, 0.0191, 0.0200, 0.0202, 0.0191, 0.0202, 0.0198,
                0.0200, 0.0198, 0.0193, 0.0192, 0.0202, 0.0192, 0.0194, 0.0199, 0.0197,
                0.0197, 0.0200, 0.0199, 0.0190, 0.0192, 0.0195, 0.0202, 0.0194, 0.0203,
                0.0201, 0.0190, 0.0192, 0.0201, 0.0200, 0.0192],
                [0.0191, 0.0197, 0.0200, 0.0190, 0.0195, 0.0198, 0.0194, 0.0192, 0.0200,
                0.0203, 0.0190, 0.0191, 0.0199, 0.0193, 0.0192, 0.0199, 0.0198, 0.0197,
                0.0193, 0.0198, 0.0192, 0.0191, 0.0199, 0.0202, 0.0192, 0.0202, 0.0198,
                0.0200, 0.0198, 0.0193, 0.0192, 0.0202, 0.0192, 0.0194, 0.0199, 0.0197,
                0.0197, 0.0200, 0.0199, 0.0190, 0.0192, 0.0195, 0.0202, 0.0194, 0.0203,
                0.0201, 0.0190, 0.0192, 0.0201, 0.0200, 0.0192]
            ]).cuda()
            support = torch.tensor([
                [-9.7030, -9.3149, -8.9268, -8.5386, -8.1505, -7.7624, -7.3743, -6.9862,
                -6.5980, -6.2099, -5.8218, -5.4337, -5.0456, -4.6574, -4.2693, -3.8812,
                -3.4931, -3.1050, -2.7168, -2.3287, -1.9406, -1.5525, -1.1644, -0.7762,
                -0.3881,  0.0000,  0.3881,  0.7762,  1.1644,  1.5525,  1.9406,  2.3287,
                2.7168,  3.1050,  3.4931,  3.8812,  4.2693,  4.6574,  5.0456,  5.4337,
                5.8218,  6.2099,  6.5980,  6.9862,  7.3743,  7.7624,  8.1505,  8.5386,
                8.9268,  9.3149,  9.7030],
                [-9.7030, -9.3149, -8.9268, -8.5386, -8.1505, -7.7624, -7.3743, -6.9862,
                -6.5980, -6.2099, -5.8218, -5.4337, -5.0456, -4.6574, -4.2693, -3.8812,
                -3.4931, -3.1050, -2.7168, -2.3287, -1.9406, -1.5525, -1.1644, -0.7762,
                -0.3881,  0.0000,  0.3881,  0.7762,  1.1644,  1.5525,  1.9406,  2.3287,
                2.7168,  3.1050,  3.4931,  3.8812,  4.2693,  4.6574,  5.0456,  5.4337,
                5.8218,  6.2099,  6.5980,  6.9862,  7.3743,  7.7624,  8.1505,  8.5386,
                8.9268,  9.3149,  9.7030],
                [-9.7030, -9.3149, -8.9268, -8.5386, -8.1505, -7.7624, -7.3743, -6.9862,
                -6.5980, -6.2099, -5.8218, -5.4337, -5.0456, -4.6574, -4.2693, -3.8812,
                -3.4931, -3.1050, -2.7168, -2.3287, -1.9406, -1.5525, -1.1644, -0.7762,
                -0.3881,  0.0000,  0.3881,  0.7762,  1.1644,  1.5525,  1.9406,  2.3287,
                2.7168,  3.1050,  3.4931,  3.8812,  4.2693,  4.6574,  5.0456,  5.4337,
                5.8218,  6.2099,  6.5980,  6.9862,  7.3743,  7.7624,  8.1505,  8.5386,
                8.9268,  9.3149,  9.7030]
            ]).cuda()
            expected = torch.tensor([
                [0.0049, 0.0198, 0.0204, 0.0202, 0.0198, 0.0202, 0.0202, 0.0199, 0.0202,
                0.0208, 0.0201, 0.0195, 0.0201, 0.0201, 0.0198, 0.0203, 0.0204, 0.0203,
                0.0200, 0.0203, 0.0199, 0.0197, 0.0205, 0.0208, 0.0197, 0.0214, 0.0204,
                0.0206, 0.0203, 0.0199, 0.0199, 0.0206, 0.0198, 0.0201, 0.0204, 0.0203,
                0.0204, 0.0206, 0.0201, 0.0197, 0.0199, 0.0204, 0.0204, 0.0205, 0.0208,
                0.0200, 0.0197, 0.0204, 0.0207, 0.0200, 0.0049],
                [0.0049, 0.0198, 0.0204, 0.0202, 0.0198, 0.0202, 0.0202, 0.0199, 0.0202,
                0.0208, 0.0202, 0.0196, 0.0201, 0.0201, 0.0198, 0.0203, 0.0204, 0.0203,
                0.0200, 0.0203, 0.0199, 0.0197, 0.0205, 0.0208, 0.0197, 0.0214, 0.0204,
                0.0206, 0.0203, 0.0199, 0.0199, 0.0206, 0.0198, 0.0201, 0.0204, 0.0203,
                0.0204, 0.0206, 0.0201, 0.0197, 0.0199, 0.0204, 0.0204, 0.0205, 0.0208,
                0.0200, 0.0197, 0.0204, 0.0206, 0.0200, 0.0049],
                [0.0049, 0.0198, 0.0204, 0.0202, 0.0198, 0.0202, 0.0202, 0.0199, 0.0202,
                0.0208, 0.0202, 0.0196, 0.0202, 0.0201, 0.0198, 0.0203, 0.0204, 0.0203,
                0.0200, 0.0203, 0.0199, 0.0197, 0.0204, 0.0208, 0.0198, 0.0214, 0.0204,
                0.0206, 0.0203, 0.0199, 0.0199, 0.0206, 0.0198, 0.0201, 0.0204, 0.0203,
                0.0204, 0.0206, 0.0201, 0.0197, 0.0199, 0.0204, 0.0204, 0.0205, 0.0208,
                0.0200, 0.0197, 0.0204, 0.0206, 0.0200, 0.0049]
            ])
            tt.assert_almost_equal(q.project(dist, support).cpu(), expected.cpu(), decimal=3)

if __name__ == "__main__":
    unittest.main()
