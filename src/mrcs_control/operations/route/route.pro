
% ---------------------------------------------------------------------------------------------------------------------

add_conf(Turnout-Pos, ConfIn, ConfIn) :-
    member(Turnout-Pos, ConfIn), !.

add_conf(Turnout-NewPos, ConfIn, _) :-
    member(Turnout-OldPos, ConfIn),
    NewPos \= OldPos, !, fail.

add_conf(Conf, ConfIn, [Conf | ConfIn]). % Dynamically add Conf if missing

% ---------------------------------------------------------------------------------------------------------------------

route(Start, End, Length, Dir, [Start, End], ConfIn, ConfOut) :-
    link(Start, End, LinkLength, Dir, ConfIn, ConfOut),
    segment(Start, StartLength), segment(End, EndLength),
    Length is LinkLength + StartLength + EndLength.

route(Start, End, Length, Dir, [Start | RemainingRoute], ConfIn, ConfOut) :-
    link(Start, Mid, LinkLength, Dir, ConfIn, ConfMid),
    segment(Start, StartLength), route(Mid, End, RemainingLength, Dir, RemainingRoute, ConfMid, ConfOut),
    Length is LinkLength + StartLength + RemainingLength.
