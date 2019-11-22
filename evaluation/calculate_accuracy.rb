require 'csv'
require 'terminal-table'

HIGH_PROBABILITY = 0.5
HIGHER_PROBABILITY = 0.7
HIGHEST_PROBABILITY = 0.9

csv = CSV.parse(File.open(File.join(File.dirname(__FILE__), 'result.csv')))[1..-1]
level_1_high_prob = csv.filter{|r| Float(r[2]) > HIGH_PROBABILITY }
level_1_higher_prob = csv.filter{|r| Float(r[2]) > HIGHER_PROBABILITY }
level_1_highest_prob = csv.filter{|r| Float(r[2]) > HIGHEST_PROBABILITY }
level_3 = csv.filter{|r| !r[5].nil? && r[5] !~ /\A[[:space:]]*\z/ }
level_3_high_prob = level_3.filter{|r| Float(r[7]) > HIGH_PROBABILITY }
level_3_higher_prob = level_3.filter{|r| Float(r[7]) > HIGHER_PROBABILITY }
level_3_highest_prob = level_3.filter{|r| Float(r[7]) > HIGHEST_PROBABILITY }
level_4 = csv.filter{|r| !r[10].nil? && r[10] !~ /\A[[:space:]]*\z/ }
level_4_high_prob = level_4.filter{|r| Float(r[12]) > HIGH_PROBABILITY }
level_4_higher_prob = level_4.filter{|r| Float(r[7]) > HIGHER_PROBABILITY }
level_4_highest_prob = level_4.filter{|r| Float(r[7]) > HIGHEST_PROBABILITY }

rows = [
  ['Probability', nil, HIGH_PROBABILITY, HIGHER_PROBABILITY, HIGHEST_PROBABILITY],
  ['Total rows ', csv.length],
  ['Rows where level 1 is correctly predicted total ', csv.filter{|r| r[0].include?(r[1]) }.length],
  ['Rows where level 1 has a good prediction ', nil, level_1_high_prob.length, level_1_higher_prob.length, level_1_highest_prob.length],
  ['Rows where level 1 has a good prediction and is correct ', nil, level_1_high_prob.filter{|r| r[0].include?(r[1]) }.length, level_1_higher_prob.filter{|r| r[0].include?(r[1]) }.length, level_1_highest_prob.filter{|r| r[0].include?(r[1]) }.length],
  ['Rows where level 3 exists ', level_3.length],
  ['Rows where level 3 is correctly predicted total ', level_3.filter{|r| r[5].include?(r[6]) }.length],
  ['Rows where level 3 has a good prediction ', nil, level_3_high_prob.length, level_3_higher_prob.length, level_3_highest_prob.length],
  ['Rows where level 3 has a good prediction and is correct ', nil, level_3_high_prob.filter{|r| r[5].include?(r[6]) }.length, level_3_higher_prob.filter{|r| r[5].include?(r[6]) }.length, level_3_highest_prob.filter{|r| r[5].include?(r[6]) }.length],
  ['Rows where level 4 exists ', level_4.length],
  ['Rows where level 4 is correctly predicted total ', level_4.filter{|r| r[10].include?(r[11]) }.length],
  ['Rows where level 4 has a good prediction ', nil, level_4_high_prob.length, level_4_higher_prob.length, level_4_highest_prob.length],
  ['Rows where level 4 has a good prediction and is correct ', nil, level_4_high_prob.filter{|r| r[10].include?(r[11]) }.length, level_4_higher_prob.filter{|r| r[10].include?(r[11]) }.length, level_4_highest_prob.filter{|r| r[10].include?(r[11]) }.length],
]
puts Terminal::Table.new :rows => rows
