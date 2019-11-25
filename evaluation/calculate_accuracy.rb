require 'csv'
require 'terminal-table'

HIGH_PROBABILITY = 0.5
HIGHER_PROBABILITY = 0.7
HIGHEST_PROBABILITY = 0.9

file_name = ARGV[0].split(File::SEPARATOR)[-1]

csv = CSV.parse(File.open(File.join(File.dirname(__FILE__), file_name)))[1..-1]

def generate_rows csv, level, id_column, pred_column, prob_column
  all_for_level = csv.select{|r| !r[id_column].nil? && r[id_column] !~ /\A[[:space:]]*\z/ }
  high_prob = all_for_level.select{|r| Float(r[prob_column]) > HIGH_PROBABILITY }
  higher_prob = all_for_level.select{|r| Float(r[prob_column]) > HIGHER_PROBABILITY }
  highest_prob = all_for_level.select{|r| Float(r[prob_column]) > HIGHEST_PROBABILITY }

  [
    ["Rows where level #{level} exists ", all_for_level.length],
    ["Rows where level #{level} is correctly predicted total ", all_for_level.select{|r| r[id_column].include?(r[pred_column]) }.length],
    ["Rows where level #{level} has a good prediction ", nil, high_prob.length, higher_prob.length, highest_prob.length],
    ["Rows where level #{level} has a good prediction and is correct ", nil, high_prob.select{|r| r[id_column].include?(r[pred_column]) }.length, higher_prob.select{|r| r[id_column].include?(r[pred_column]) }.length, highest_prob.select{|r| r[id_column].include?(r[pred_column]) }.length],
    ['Accuracy', nil, (high_prob.select{|r| r[id_column].include?(r[pred_column]) }.length.to_f/high_prob.length).round(2), (higher_prob.select{|r| r[id_column].include?(r[pred_column]) }.length.to_f/higher_prob.length).round(2), (highest_prob.select{|r| r[id_column].include?(r[pred_column]) }.length.to_f/highest_prob.length).round(2)],
  ]
end

rows = [
  ['Probability', nil, HIGH_PROBABILITY, HIGHER_PROBABILITY, HIGHEST_PROBABILITY],
  *generate_rows(csv, 1, 0, 1, 2),
  *generate_rows(csv, 3, 5, 6, 7),
  *generate_rows(csv, 4, 10, 11, 12)
]
puts Terminal::Table.new :rows => rows
