from mmobot.test.MockMember import MockMember


def test_MockMember_initialize():
    member = MockMember(1, 'member_name')
    assert member.id is not None
    assert member.id == 1
    assert member.nick is not None
    assert member.nick == 'member_name'
    assert member.mention is not None
    assert member.mention == '<@1>'


def test_MockMember_eq_sameMember():
    member1 = MockMember(1, 'member_name')
    member2 = MockMember(1, 'member_name')
    assert member1 == member2

    member1 = MockMember(1, 'member1')
    member2 = MockMember(1, 'member2')
    assert member1 == member2


def test_MockMember_eq_differentMember():
    member1 = MockMember(1, 'member_name')
    member2 = MockMember(2, 'member_name')
    assert member1 != member2

    member1 = MockMember(1, 'member1')
    member2 = MockMember(2, 'member2')
    assert member1 != member2
