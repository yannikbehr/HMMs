import cthmm
import pytest
import numpy

EPS = 1e-7

@pytest.fixture
def small_hmm():
    """Create small HMM and basic emission sequence for testing of basic functionality"""
    A = numpy.array([[0.9,0.1],[0.4,0.6]])
    B = numpy.array([[0.9,0.1],[0.2,0.8]])
    pi = numpy.array( [0.8,0.2] )
    hmm = cthmm.HMM(A,B,pi)

    emissions = numpy.array([0,1])
    return ( hmm, emissions )

@pytest.fixture
def short_emission( small_hmm ):
    """Return HMM and medium emission sequence"""
    hmm, em = small_hmm
    em = numpy.array([0,1,1])
    return (hmm, em)


@pytest.fixture
def medium_emission( small_hmm ):
    """Return HMM and medium emission sequence"""
    hmm, em = small_hmm
    em = numpy.array([0,1,0,1,1])
    return (hmm, em)

@pytest.fixture
def long_emission( small_hmm ):
    """Return HMM and longer emission sequence"""
    hmm, em = small_hmm
    em = numpy.array([0,0,0,1,1,0,1,1,0,0,0,0,0,1,0,0,1,1,0,0,0,1,0,1,1,1,1,0,0,1,1,1])
    return (hmm, em)

def test_froward( small_hmm ):
    """Test forward algorithm"""
    hmm, em = small_hmm

    A = numpy.array( [[0.72,0.04],[0.0664,0.0768]] )
    X = numpy.exp( hmm.forward(em) )

    assert float_equal_mat( A, X )

def test_backward( small_hmm ):
    """Test backward algorithm"""
    hmm, em = small_hmm

    A = numpy.array( [[0.17,0.52],[1,1]] )
    X = numpy.exp( hmm.backward(em) )

    assert float_equal_mat( A, X )

def test_emission_estimate( small_hmm ):
    """Test emission_estimate function"""
    hmm, em = small_hmm

    a = 0.1432
    x = numpy.exp( hmm.emission_estimate(em) )

    assert float_equal( a, x )

def test_random_vector_and_log_sum( small_hmm ):
    """test if random vector sum to one by using log_sum function"""
    hmm, em = small_hmm

    size = 1234
    vec = cthmm.get_random_vector(size)
    a = numpy.exp( hmm.log_sum( numpy.log(vec)  ) )

    assert float_equal( a, 1 )

def test_random_vector_and_log_sum_elem( small_hmm ):
    """test if random vector sum to one by using repeatedly log_sum_elem function"""
    hmm, em = small_hmm

    size = 1234
    vec = cthmm.get_random_vector ( size )
    a = 0
    for num in vec:
        a = numpy.exp(  hmm.log_sum_elem( numpy.log(a), numpy.log(num) ) )

    assert float_equal( a, 1 )

def test_viterbi_p( medium_emission ):
    """Test viterbi algorithm probability of most likely sequence"""
    hmm, em = medium_emission

    p, seq = hmm.viterbi( em )
    out_p = 0.0020155392

    assert float_equal( numpy.exp(p), out_p )

def test_viterbi_seq( medium_emission ):
    """Test viterbi algorithm sequence"""
    hmm, em = medium_emission

    p, seq = hmm.viterbi( em )
    out_seq = numpy.array([0,0,0,1,1])

    assert float_equal_mat( seq, out_seq )

def test_viterbi_long_seq( long_emission ):
    """Test viterbi algorithm sequence"""
    hmm, em = long_emission

    p, seq = hmm.viterbi( em )
    out_seq = numpy.array( [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1] )

    assert float_equal_mat( seq, out_seq )

@pytest.fixture
def ab( short_emission ):
    """Return outputs from forward and backward algorithms"""
    hmm, em = short_emission
    alpha = hmm.forward(em)
    beta = hmm.backward(em)
    return (alpha, beta)

def test_single_state_prob( short_emission, ab ):
    """Test single_state_prob function"""
    hmm, em = short_emission
    alpha, beta = ab
    gamma = hmm.single_state_prob( alpha, beta )
    gamma_out = numpy.array( [[ 0.79978135, 0.20021865],[ 0.22036545,0.77963455],[ 0.17663595,0.82336405]] )

    assert float_equal_mat( numpy.exp(gamma), gamma_out )

def test_double_state_prob( short_emission, ab ):
    """Test double_state_prob function"""
    hmm, em = short_emission
    alpha, beta = ab
    ksi = hmm.double_state_prob( alpha, beta, em )[1,:]
    ksi_out = numpy.array( [[ 0.11666406,0.10370139],[ 0.05997189,0.71966266]] )

    assert float_equal_mat( numpy.exp(ksi), ksi_out )


@pytest.fixture
def small_random_hmm():
    """Create random hmm of two hidden states and two output varaibles."""
    return cthmm.HMM( *cthmm.get_random_parameters(2,2) )

@pytest.fixture
def hmm_small_out():
    """Desired training output for sequence [[0,1,1]]"""
    A = numpy.array([[0,1],[0,1]])
    B = numpy.array([[1,0],[0,1]])
    pi = numpy.array( [1,0] )
    return cthmm.HMM(A,B,pi)

@pytest.fixture
def hmm_cycle_out():
    """Desired training output for sequence [[0,1,1]]"""
    A = numpy.array([[0,1],[1,0]])
    B = numpy.array([[1,0],[0,1]])
    pi = numpy.array( [0.5,0.5] )
    return cthmm.HMM(A,B,pi)

def test_baum_welch_small( small_random_hmm, hmm_small_out ):
    """Test if baum_welch algorithm converge to the right parameters"""
    hmm = small_random_hmm
    data = numpy.array([[0,1,1]]);
    hmm.baum_welch( data , 20 )

    assert compare_parameters( hmm, hmm_small_out, 1e-2 )

def test_baum_welch_small_multiple_data( small_random_hmm, hmm_small_out ):
    """Test if baum_welch algorithm converge to the right parameters"""
    hmm = small_random_hmm
    data = numpy.array([[0,1,1],[0,1,1],[0,1,1],[0,1,1],[0,1,1]]);
    hmm.baum_welch( data , 20 )

    assert compare_parameters( hmm, hmm_small_out, 1e-2 )

def test_baum_welch_cykle( small_random_hmm, hmm_cycle_out ):
    """Test if baum_welch algorithm converge to the right parameters"""
    #TODO sometimes (1/5 cases) fall in the local optima, examine, if it is ok behaviour
    hmm = small_random_hmm
    data = numpy.array([[0,1,0,1,0,1],[1,0,1,0,1,0],[1,0,1,0,1,0],[0,1,0,1,0,1],[0,1,0,1,0,1],[1,0,1,0,1,0]]);
    hmm.baum_welch( data , 20 )

    assert compare_parameters( hmm, hmm_cycle_out, 1e-2 )


def compare_parameters( m1, m2, eps ):
    """Compare whole hmm parameters"""

    #Notice: sort_rows is needed, because any permutation of hidden states is acceptable
    ok  = float_equal_mat( sort_mat(m1.a),  sort_mat(m2.a), eps )
    ok &= float_equal_mat( sort_mat(m1.b),  sort_mat(m2.b), eps )
    ok &= float_equal_mat( numpy.sort(m1.pi), numpy.sort(m2.pi),eps )

    return ok

def get_hash( a ):
    """Return hash of the numpy vector or the number itself, if it is float"""
    val = 0
    for i in a:
        val += i
        val *= 10
    return val

def sort_rows( m ):
    """Sort rows in numpy array in some deterministic order"""
    sm = numpy.zeros( m.shape[0] )
    for i,a in enumerate(m):
        sm[i] = get_hash( a )
    return m[ numpy.argsort( sm ),:]

def sort_mat( m ):
    """Sort matrix in the way, so the all hidden state permutation will form the same matrix"""
    print("m")
    print(m)
    m = sort_rows(m)
    print(m)
    m = sort_rows(m.T)
    print(m)
    return m

def float_equal( a , b , eps = EPS):
    """Compare two floats with possible error EPS"""
    print(a,b)
    return numpy.fabs(a-b) < eps

def float_equal_mat( A , B, eps = EPS):
    """Takes two numpy arrays or vectors and tells if they are equal (with possible EPS error caused by double imprecision)"""
    print("#####Compare_matrices#####")
    print(A)
    print("-"*10)
    print(B)
    print("#"*10)
    for a,b in zip( A.flatten(), B.flatten() ):
        if numpy.fabs(a-b) > eps :
            print("Do not equal!")
            return False
    return True

